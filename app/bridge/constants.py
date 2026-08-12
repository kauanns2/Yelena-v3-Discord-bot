"""Constantes do Bridge."""

from enum import Enum


class PlatformId(str, Enum):
    DISCORD = "discord"
    TELEGRAM = "telegram"
    HTTP = "http"
    CUSTOM = "custom"


class ContinuityNamespace(str, Enum):
    MEMORY_SNAPSHOT = "memory_snapshot"
    KNOWLEDGE_SNAPSHOT = "knowledge_snapshot"
    PERSONALITY_SNAPSHOT = "personality_snapshot"
    EMOTION_SNAPSHOT = "emotion_snapshot"
    SESSION = "session"
    USER = "user"
    EVOLUTION = "evolution"
    SYSTEM = "system"
    CUSTOM = "custom"


DEFAULT_CONTINUITY_DIR = ".yelena_continuity"
