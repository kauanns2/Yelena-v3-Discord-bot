"""Fachada do módulo Voice."""

from __future__ import annotations

import asyncio
import logging
import os
import random
import re
from pathlib import Path
from typing import Any

from app.voice.profile import prepare_spoken_text
from app.voice.providers.edge import EdgeTTSProvider

logger = logging.getLogger(__name__)

AUDIO_REQUEST_RE = re.compile(
    r"\b(áudio|audio|voz|voice|manda (um )?áudio|envie (um )?áudio|"
    r"responde em áudio|fala em áudio|manda voz|em áudio)\b",
    re.I,
)


def wants_audio(text: str, *, auto_rate: float | None = None) -> bool:
    if AUDIO_REQUEST_RE.search(text or ""):
        return True
    try:
        rate = float(os.getenv("YELENA_VOICE_AUTO", "0") or "0") if auto_rate is None else auto_rate
    except ValueError:
        rate = 0.0
    rate = max(0.0, min(1.0, float(rate)))
    return rate > 0 and random.random() < rate


class VoiceManager:
    """API pública do módulo de voz."""

    def __init__(self) -> None:
        self._enabled = (os.getenv("YELENA_VOICE_ENABLED", "true") or "true").strip().lower() in {
            "1",
            "true",
            "yes",
            "on",
        }
        self._provider = EdgeTTSProvider()
        self._started = False
        self._metrics = {"synth_ok": 0, "synth_fail": 0}

    @property
    def is_enabled(self) -> bool:
        return self._enabled

    def start(self) -> None:
        self._started = True
        logger.info("voice module started provider=%s", self._provider.id)

    def stop(self) -> None:
        self._started = False

    def synthesize(self, text: str, *, emotion: str | None = None) -> Path | None:
        if not self._enabled:
            return None
        clean = prepare_spoken_text(text, emotion=emotion)
        if not clean:
            return None
        try:
            return asyncio.run(self._provider.synthesize(clean))
        except RuntimeError:
            try:
                import concurrent.futures

                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                    return pool.submit(
                        lambda: asyncio.run(self._provider.synthesize(clean))
                    ).result(timeout=60)
            except Exception:
                logger.exception("synthesize failed")
                self._metrics["synth_fail"] += 1
                return None
        except Exception:
            logger.exception("synthesize failed")
            self._metrics["synth_fail"] += 1
            return None

    async def synthesize_async(self, text: str, *, emotion: str | None = None) -> Path | None:
        if not self._enabled:
            return None
        clean = prepare_spoken_text(text, emotion=emotion)
        if not clean:
            return None
        try:
            path = await self._provider.synthesize(clean)
            if path:
                self._metrics["synth_ok"] += 1
            else:
                self._metrics["synth_fail"] += 1
            return path
        except Exception:
            logger.exception("synthesize_async failed")
            self._metrics["synth_fail"] += 1
            return None

    def health(self) -> dict[str, Any]:
        return {
            "status": "healthy" if self._started else "stopped",
            "enabled": self._enabled,
            "provider": self._provider.id,
            "metrics": dict(self._metrics),
            "sends_chat_files": False,
        }
