"""Providers de TTS."""

from app.voice.providers.base import TTSProvider
from app.voice.providers.edge import EdgeTTSProvider

__all__ = ["TTSProvider", "EdgeTTSProvider"]
