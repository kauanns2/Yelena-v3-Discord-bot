"""TTS e detecção de pedido de áudio."""

from __future__ import annotations

import asyncio
import logging
import os
import random
import re
import tempfile
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

AUDIO_REQUEST_RE = re.compile(
    r"\b(áudio|audio|voz|voice|manda (um )?áudio|envie (um )?áudio|"
    r"responde em áudio|fala em áudio|manda voz|em áudio)\b",
    re.I,
)


def wants_audio(text: str, *, auto_rate: float | None = None) -> bool:
    if AUDIO_REQUEST_RE.search(text or ""):
        return True
    rate = auto_rate
    if rate is None:
        try:
            rate = float(os.getenv("YELENA_VOICE_AUTO", "0") or "0")
        except ValueError:
            rate = 0.0
    rate = max(0.0, min(1.0, float(rate)))
    return rate > 0 and random.random() < rate


class VoiceManager:
    """Gera arquivos de áudio a partir de texto (edge-tts)."""

    def __init__(self) -> None:
        self._enabled = (os.getenv("YELENA_VOICE_ENABLED", "true") or "true").strip().lower() in {
            "1",
            "true",
            "yes",
            "on",
        }
        self._voice = (
            os.getenv("YELENA_TTS_VOICE", "pt-BR-FranciscaNeural") or "pt-BR-FranciscaNeural"
        ).strip()
        self._started = False
        self._metrics = {"synth_ok": 0, "synth_fail": 0}

    @property
    def is_enabled(self) -> bool:
        return self._enabled

    def start(self) -> None:
        self._started = True
        logger.info("voice system started enabled=%s voice=%s", self._enabled, self._voice)

    def stop(self) -> None:
        self._started = False

    def synthesize(self, text: str) -> Path | None:
        """Gera MP3 temporário. Retorna path ou None."""
        if not self._enabled:
            return None
        clean = (text or "").strip()
        if not clean:
            return None
        # limite de segurança TTS
        if len(clean) > 500:
            clean = clean[:497].rstrip() + "..."

        try:
            return asyncio.run(self._synthesize_async(clean))
        except RuntimeError:
            # já existe loop (ex.: dentro do discord async)
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # cria task síncrona via future em thread — fallback simples
                    import concurrent.futures

                    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                        return pool.submit(lambda: asyncio.run(self._synthesize_async(clean))).result(
                            timeout=60
                        )
                return loop.run_until_complete(self._synthesize_async(clean))
            except Exception:
                logger.exception("voice synthesize failed")
                self._metrics["synth_fail"] += 1
                return None
        except Exception:
            logger.exception("voice synthesize failed")
            self._metrics["synth_fail"] += 1
            return None

    async def synthesize_async(self, text: str) -> Path | None:
        if not self._enabled:
            return None
        clean = (text or "").strip()
        if not clean:
            return None
        if len(clean) > 500:
            clean = clean[:497].rstrip() + "..."
        try:
            return await self._synthesize_async(clean)
        except Exception:
            logger.exception("voice synthesize_async failed")
            self._metrics["synth_fail"] += 1
            return None

    async def _synthesize_async(self, text: str) -> Path | None:
        try:
            import edge_tts
        except ImportError:
            logger.error("edge-tts not installed")
            self._metrics["synth_fail"] += 1
            return None

        fd, path_str = tempfile.mkstemp(prefix="yelena_tts_", suffix=".mp3")
        os.close(fd)
        path = Path(path_str)
        try:
            communicate = edge_tts.Communicate(text, self._voice)
            await communicate.save(str(path))
            if not path.exists() or path.stat().st_size < 32:
                path.unlink(missing_ok=True)
                self._metrics["synth_fail"] += 1
                return None
            self._metrics["synth_ok"] += 1
            return path
        except Exception:
            path.unlink(missing_ok=True)
            raise

    def health(self) -> dict[str, Any]:
        return {
            "status": "healthy" if self._started else "stopped",
            "enabled": self._enabled,
            "voice": self._voice,
            "metrics": dict(self._metrics),
        }
