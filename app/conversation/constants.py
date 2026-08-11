"""Constantes do Conversation System."""

from enum import Enum


class IntentType(str, Enum):
    GREETING = "greeting"
    FAREWELL = "farewell"
    QUESTION = "question"
    REQUEST = "request"
    STATEMENT = "statement"
    CONFIRMATION = "confirmation"
    DENIAL = "denial"
    CORRECTION = "correction"
    CLARIFICATION = "clarification"
    FEEDBACK = "feedback"
    EMOTIONAL = "emotional"
    TECHNICAL = "technical"
    ACTION = "action"
    UNKNOWN = "unknown"


class TurnRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class SessionStatus(str, Enum):
    ACTIVE = "active"
    IDLE = "idle"
    WAITING_CLARIFICATION = "waiting_clarification"
    CLOSED = "closed"
    EXPIRED = "expired"


DEFAULT_SESSION_TTL = 3600.0
DEFAULT_MAX_TURNS = 100
