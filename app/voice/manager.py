"""Fachada do módulo Voice."""

from __future__ import annotations

import asyncio
import logging
import os
from pathlib import Path
from typing import Any

from app.voice.profile import prepare_spoken_text
from app.voice.providers.edge import EdgeTTSProvider
from app.voice.wants import wants_audio

logger = logging.getLogger(__name__)

__all__ = ["VoiceManager", "wants_audio"]


class VoiceManager:
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
        }
