"""Sistema de health do Core."""

from __future__ import annotations

import logging
import time
from typing import Any, Callable, Awaitable

from app.core.constants import HealthStatus
from app.core.protocols import HealthCheckResult
from app.core.types import ModuleId

logger = logging.getLogger(__name__)

HealthChecker = Callable[[], Awaitable[HealthCheckResult]]


class HealthManager:
    """Agrega health checks do Core e dos módulos."""

    def __init__(self) -> None:
        self._checkers: dict[str, HealthChecker] = {}

    def register(self, name: str, checker: HealthChecker) -> None:
        self._checkers[name] = checker

    def unregister(self, name: str) -> None:
        self._checkers.pop(name, None)

    async def check_one(self, name: str) -> HealthCheckResult:
        checker = self._checkers.get(name)
        if checker is None:
            return HealthCheckResult(
                status=HealthStatus.UNKNOWN,
                message=f"No health checker for: {name}",
            )
        start = time.perf_counter()
        try:
            result = await checker()
            result.latency_ms = (time.perf_counter() - start) * 1000
            return result
        except Exception as exc:
            latency = (time.perf_counter() - start) * 1000
            logger.exception("health check failed", extra={"checker": name})
            return HealthCheckResult(
                status=HealthStatus.UNHEALTHY,
                message=str(exc),
                latency_ms=latency,
                details={"error_type": type(exc).__name__},
            )

    async def check_all(self) -> dict[str, HealthCheckResult]:
        results: dict[str, HealthCheckResult] = {}
        for name in self._checkers:
            results[name] = await self.check_one(name)
        return results

    async def aggregate(self) -> HealthCheckResult:
        results = await self.check_all()
        if not results:
            return HealthCheckResult(
                status=HealthStatus.UNKNOWN,
                message="No health checkers registered",
            )

        statuses = [r.status for r in results.values()]
        if any(s == HealthStatus.UNHEALTHY for s in statuses):
            overall = HealthStatus.UNHEALTHY
        elif any(s == HealthStatus.DEGRADED for s in statuses):
            overall = HealthStatus.DEGRADED
        elif any(s == HealthStatus.UNKNOWN for s in statuses):
            overall = HealthStatus.DEGRADED
        else:
            overall = HealthStatus.HEALTHY

        return HealthCheckResult(
            status=overall,
            message=f"Aggregated health from {len(results)} checkers",
            details={name: r.to_dict() for name, r in results.items()},
        )
