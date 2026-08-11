"""Constantes do Cognitive Context."""

from enum import Enum


class ContextItemSource(str, Enum):
    MEMORY = "memory"
    KNOWLEDGE = "knowledge"
    NEURAL = "neural"
    CONVERSATION = "conversation"
    EMOTION = "emotion"
    PERSONALITY = "personality"
    SYSTEM = "system"
    USER = "user"


class ContextPriority(int, Enum):
    LOW = 10
    NORMAL = 50
    HIGH = 80
    CRITICAL = 100


DEFAULT_TOKEN_BUDGET = 2000
DEFAULT_MAX_ITEMS = 30
DEFAULT_MIN_RELEVANCE = 0.15
