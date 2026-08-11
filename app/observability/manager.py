"""Observability Manager."""

from __future__ import annotations

import logging
from typing import Any, Callable

from app.observability.alerts import AlertManager
from app.observability.constants import LogLevel, AlertSeverity, HealthStatus
from app.observability.diagnostics import DiagnosticsEngine
from app.observability.health import HealthAggregator
from app.observability.logging import StructuredLogger
from app.observability.metrics import MetricsRegistry
from app.observability.models.diagnostic import DiagnosticReport
from app.observability.models.health import HealthReport
from app.observability.tracing import Tracer

logger = logging.getLogger(__name__)


class ObservabilityManager:
    """Ponto central de observabilidade.

    Coleta sinais. Não decide recuperação sozinho.
    """

    def __init__(self) -> None:
        self.logs = StructuredLogger("yelena")
        self.metrics = MetricsRegistry()
        self.tracer = Tracer()
        self.health = HealthAggregator()
        self.alerts = AlertManager()
        self.diagnostics = DiagnosticsEngine()
        self._started = False

    @property
    def is_started(self) -> bool:
        return self._started

    def start(self) -> None:
        self._started = True
        self.metrics.incr("observability_starts")
        self.logs.info("observability system started", module="observability")
        logger.info("observability system started")

    def stop(self) -> None:
        self._started = False
        self.logs.info("observability system stopped", module="observability")

    def register_health(self, name: str, checker: Callable[[], dict[str, Any]]) -> None:
        self.health.register(name, checker)

    def log(self, message: str, level: LogLevel = LogLevel.INFO, **kwargs: Any) -> None:
        self.logs.log(message, level, **kwargs)
        if level in {LogLevel.ERROR, LogLevel.CRITICAL}:
            self.metrics.incr("errors_total")

    def check_health(self) -> HealthReport:
        report = self.health.check()
        self.metrics.set_gauge("health_status", {
            HealthStatus.HEALTHY: 1,
            HealthStatus.DEGRADED: 0.5,
            HealthStatus.UNHEALTHY: 0,
            HealthStatus.UNKNOWN: -1,
        }.get(report.status, -1))
        return report

    def diagnose(self) -> DiagnosticReport:
        health = self.check_health()
        return self.diagnostics.build(health, self.metrics.snapshot())

    def raise_alert(
        self,
        title: str,
        *,
        severity: AlertSeverity = AlertSeverity.WARNING,
        message: str = "",
        source: str = "observability",
    ) -> None:
        alert = self.alerts.fire(title, severity=severity, message=message, source=source)
        if alert:
            self.metrics.incr("alerts_fired", severity=severity.value)
            self.logs.warning(f"alert: {title}", module="observability", severity=severity.value)

    def health_status(self) -> dict[str, Any]:
        return {
            "status": "healthy" if self._started else "stopped",
            "metrics": self.metrics.snapshot(),
            "active_alerts": len(self.alerts.active()),
            "recent_logs": len(self.logs.recent(10)),
        }
