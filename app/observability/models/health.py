"""Health report."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
import time

from app.observability.constants import HealthStatus


@dataclass(slots=True)
class ComponentHealth:
    name: str
    status: HealthStatus = HealthStatus.UNKNOWN
    message: str = ""
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "status": self.status.value,
            "message": self.message,
            "details": self.details,
        }


@dataclass(slots=True)
class HealthReport:
    status: HealthStatus = HealthStatus.UNKNOWN
    components: list[ComponentHealth] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status.value,
            "components": [c.to_dict() for c in self.components],
            "timestamp": self.timestamp,
        }
