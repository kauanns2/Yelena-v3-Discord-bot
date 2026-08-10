"""Constantes do Core."""

from enum import Enum


class LifecycleState(str, Enum):
    """Estados do ciclo de vida da aplicação e dos módulos."""

    CREATED = "created"
    BOOTSTRAPPING = "bootstrapping"
    STARTING = "starting"
    RUNNING = "running"
    DEGRADED = "degraded"
    STOPPING = "stopping"
    STOPPED = "stopped"
    FAILED = "failed"


class HealthStatus(str, Enum):
    """Status de saúde."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class ModulePriority(int, Enum):
    """Prioridade de inicialização (menor = mais cedo)."""

    CRITICAL = 0
    HIGH = 10
    NORMAL = 50
    LOW = 100
    BACKGROUND = 200


VALID_TRANSITIONS: dict[LifecycleState, set[LifecycleState]] = {
    LifecycleState.CREATED: {LifecycleState.BOOTSTRAPPING, LifecycleState.FAILED},
    LifecycleState.BOOTSTRAPPING: {LifecycleState.STARTING, LifecycleState.FAILED},
    LifecycleState.STARTING: {
        LifecycleState.RUNNING,
        LifecycleState.DEGRADED,
        LifecycleState.FAILED,
    },
    LifecycleState.RUNNING: {
        LifecycleState.DEGRADED,
        LifecycleState.STOPPING,
        LifecycleState.FAILED,
    },
    LifecycleState.DEGRADED: {
        LifecycleState.RUNNING,
        LifecycleState.STOPPING,
        LifecycleState.FAILED,
    },
    LifecycleState.STOPPING: {LifecycleState.STOPPED, LifecycleState.FAILED},
    LifecycleState.STOPPED: set(),
    LifecycleState.FAILED: {LifecycleState.STOPPING, LifecycleState.STOPPED},
}

DEFAULT_SHUTDOWN_TIMEOUT = 30.0
DEFAULT_HEALTH_TIMEOUT = 5.0
