"""Estado global controlado do Core."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
import time

from app.core.constants import LifecycleState, HealthStatus


@dataclass(slots=True)
class CoreState:
    """Estado tipado e controlado do Core."""

    lifecycle: LifecycleState = LifecycleState.CREATED
    health: HealthStatus = HealthStatus.UNKNOWN
    started_at: float | None = None
    stopped_at: float | None = None
    environment: str = "development"
    correlation_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)

    @property
    def uptime_seconds(self) -> float | None:
        if self.started_at is None:
            return None
        end = self.stopped_at if self.stopped_at is not None else time.time()
        return max(0.0, end - self.started_at)

    @property
    def is_operational(self) -> bool:
        return self.lifecycle in {LifecycleState.RUNNING, LifecycleState.DEGRADED}

    def to_dict(self) -> dict[str, Any]:
        return {
            "lifecycle": self.lifecycle.value,
            "health": self.health.value,
            "started_at": self.started_at,
            "stopped_at": self.stopped_at,
            "uptime_seconds": self.uptime_seconds,
            "environment": self.environment,
            "correlation_id": self.correlation_id,
            "metadata": self.metadata,
            "errors": list(self.errors),
        }
