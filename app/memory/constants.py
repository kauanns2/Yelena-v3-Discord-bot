"""Constantes do Memory System."""

from enum import Enum


class MemoryType(str, Enum):
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PREFERENCE = "preference"
    AUTOBIOGRAPHICAL = "autobiographical"
    EMOTIONAL = "emotional"
    WORKING = "working"
    PROCEDURAL = "procedural"
    RELATIONAL = "relational"
    FACTUAL = "factual"
    CONTEXTUAL = "contextual"


class MemoryStatus(str, Enum):
    ACTIVE = "active"
    CONSOLIDATED = "consolidated"
    ARCHIVED = "archived"
    FORGOTTEN = "forgotten"
    DECAYING = "decaying"


class PrivacyLevel(str, Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    PRIVATE = "private"
    SENSITIVE = "sensitive"
    RESTRICTED = "restricted"


class MemorySource(str, Enum):
    CONVERSATION = "conversation"
    USER = "user"
    SYSTEM = "system"
    INFERENCE = "inference"
    IMPORT = "import"
    LEARNING = "learning"


DEFAULT_IMPORTANCE = 0.5
DEFAULT_CONFIDENCE = 0.7
DEFAULT_STRENGTH = 1.0
DEFAULT_DECAY_RATE = 0.01
DEFAULT_WORKING_TTL = 1800.0
DEFAULT_MAX_RETRIEVAL = 20
