"""Constantes do Reasoning System."""

from enum import Enum


class DecisionStatus(str, Enum):
    PENDING = "pending"
    ANALYZING = "analyzing"
    DECIDED = "decided"
    NEEDS_INFO = "needs_info"
    FAILED = "failed"
    CANCELLED = "cancelled"


class StrategyType(str, Enum):
    DIRECT = "direct"
    COMPARE = "compare"
    DECOMPOSE = "decompose"
    HYPOTHESIZE = "hypothesize"
    PLAN = "plan"
    CONSERVATIVE = "conservative"


class RiskLevel(str, Enum):
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


DEFAULT_TIMEOUT = 10.0
DEFAULT_MAX_ALTERNATIVES = 5
DEFAULT_MIN_CONFIDENCE = 0.3
