"""TTS via edge-tts (provisório até voice clone)."""

from __future__ import annotations

import logging
import os
import tempfile
from pathlib import Path

from app.voice.profile import DEFAULT_PITCH, DEFAULT_RATE, DEFAULT_VOICE, DEFAULT_VOLUME
from app.voice.providers.base import TTSProvider

logger = logging.getLogger(__name__)


class EdgeTTSProvider(TTSProvider):
    def __init__(
        self,
        voice: str | None = None,
        rate: str | None = None,
        pitch: str | None = None,
        volume: str | None = None,
    ) -> None:
        self._voice = voice or DEFAULT_VOICE
        self._rate = rate or DEFAULT_RATE
        self._pitch = pitch or DEFAULT_PITCH
        self._volume = volume or DEFAULT_VOLUME

    @property
    def id(self) -> str:
        return "edge_tts"

    async def synthesize(self, text: str) -> Path | None:
        try:
            import edge_tts
        except ImportError:
            logger.error("edge-tts not installed")
            return None

        fd, path_str = tempfile.mkstemp(prefix="yelena_tts_", suffix=".mp3")
        os.close(fd)
        path = Path(path_str)
        try:
            communicate = edge_tts.Communicate(
                text,
                self._voice,
                rate=self._rate,
                pitch=self._pitch,
                volume=self._volume,
            )
            await communicate.save(str(path))
            if path.exists() and path.stat().st_size >= 32:
                return path
            path.unlink(missing_ok=True)
            return None
        except Exception:
            path.unlink(missing_ok=True)
            logger.exception("edge tts failed")
            return None
