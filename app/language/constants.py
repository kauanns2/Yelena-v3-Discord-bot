"""Constantes do Language System."""

from enum import Enum


class OutputFormat(str, Enum):
    TEXT = "text"
    MARKDOWN = "markdown"
    STRUCTURED = "structured"


class GenerationStatus(str, Enum):
    SUCCESS = "success"
    FALLBACK = "fallback"
    FAILED = "failed"
    CANCELLED = "cancelled"


class LengthHint(str, Enum):
    SHORT = "short"
    MEDIUM = "medium"
    LONG = "long"


LENGTH_LIMITS = {
    LengthHint.SHORT: 120,
    LengthHint.MEDIUM: 400,
    LengthHint.LONG: 1200,
}
