"""Constantes do Action System."""

from enum import Enum


class RiskLevel(str, Enum):
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ActionStatus(str, Enum):
    PENDING = "pending"
    VALIDATING = "validating"
    AWAITING_CONFIRMATION = "awaiting_confirmation"
    AUTHORIZED = "authorized"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"
    DENIED = "denied"
    TIMEOUT = "timeout"


class ToolCategory(str, Enum):
    SYSTEM = "system"
    DATA = "data"
    NETWORK = "network"
    FILE = "file"
    EXTERNAL = "external"
    UTILITY = "utility"
    CUSTOM = "custom"


DEFAULT_TIMEOUT = 30.0
DEFAULT_MAX_RETRIES = 2
