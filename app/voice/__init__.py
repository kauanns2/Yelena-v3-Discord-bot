"""Módulo Voice — voz e ligação da Yelena."""

from app.voice.manager import VoiceManager, wants_audio
from app.voice.profile import VOICE_BRIEF, prepare_spoken_text

__all__ = ["VoiceManager", "wants_audio", "VOICE_BRIEF", "prepare_spoken_text"]
