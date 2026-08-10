"""Constantes da Neural Web."""

from enum import Enum


class NodeType(str, Enum):
    MODULE = "module"
    SERVICE = "service"
    ENTITY = "entity"
    CONTEXT = "context"
    SIGNAL_HUB = "signal_hub"
    CUSTOM = "custom"


class EdgeType(str, Enum):
    DEPENDENCY = "dependency"
    RELATION = "relation"
    SIGNAL = "signal"
    CONTEXT = "context"
    DATA_FLOW = "data_flow"
    CUSTOM = "custom"


class SignalType(str, Enum):
    EVENT = "event"
    REQUEST = "request"
    RESPONSE = "response"
    STATE = "state"
    CONTROL = "control"
    NOTIFICATION = "notification"


class SignalPriority(int, Enum):
    LOW = 10
    NORMAL = 50
    HIGH = 80
    CRITICAL = 100


class NodeStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DEGRADED = "degraded"
    SUSPENDED = "suspended"


DEFAULT_TTL = 30.0
DEFAULT_MAX_HOPS = 8
DEFAULT_MAX_QUEUE = 1000
