"""Constantes do Security System."""

from enum import Enum


class DecisionEffect(str, Enum):
    ALLOW = "allow"
    DENY = "deny"
    CHALLENGE = "challenge"  # requires extra confirmation


class IdentityType(str, Enum):
    USER = "user"
    ADMIN = "admin"
    SYSTEM = "system"
    SERVICE = "service"
    ANONYMOUS = "anonymous"


class RiskLevel(str, Enum):
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# Admin principal — você
DEFAULT_ADMIN_ID = "admin"

# Fail-closed em produção
DEFAULT_FAIL_CLOSED = True
