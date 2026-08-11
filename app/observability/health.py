"""Health aggregation."""

from __future__ import annotations

from typing import Any, Callable

from app.observability.constants import HealthStatus
from app.observability.models.health import HealthReport, ComponentHealth

HealthChecker = Callable[[], dict[str, Any]]


class HealthAggregator:
    def __init__(self) -> None:
        self._checkers: dict[str, HealthChecker] = {}

    def register(self, name: str, checker: HealthChecker) -> None:
        self._checkers[name] = checker

    def unregister(self, name: str) -> None:
        self._checkers.pop(name, None)

    def check(self) -> HealthReport:
        components: list[ComponentHealth] = []
        statuses: list[HealthStatus] = []

        for name, checker in self._checkers.items():
            try:
                data = checker() or {}
                raw = str(data.get("status", "unknown")).lower()
                try:
                    status = HealthStatus(raw)
                except ValueError:
                    status = HealthStatus.UNKNOWN
                components.append(
                    ComponentHealth(
                        name=name,
                        status=status,
                        message=str(data.get("message", "")),
                        details=data,
                    )
                )
                statuses.append(status)
            except Exception as exc:
                components.append(
                    ComponentHealth(
                        name=name,
                        status=HealthStatus.UNHEALTHY,
                        message=str(exc),
                    )
                )
                statuses.append(HealthStatus.UNHEALTHY)

        if not statuses:
            overall = HealthStatus.UNKNOWN
        elif any(s == HealthStatus.UNHEALTHY for s in statuses):
            overall = HealthStatus.UNHEALTHY
        elif any(s == HealthStatus.DEGRADED for s in statuses):
            overall = HealthStatus.DEGRADED
        elif any(s == HealthStatus.UNKNOWN for s in statuses):
            overall = HealthStatus.DEGRADED
        else:
            overall = HealthStatus.HEALTHY

        return HealthReport(status=overall, components=components)
