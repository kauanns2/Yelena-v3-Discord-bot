"""Diagnostics builder."""

from __future__ import annotations

from typing import Any

from app.observability.constants import HealthStatus
from app.observability.models.diagnostic import DiagnosticReport
from app.observability.models.health import HealthReport


class DiagnosticsEngine:
    def build(
        self,
        health: HealthReport,
        metrics: dict[str, float],
    ) -> DiagnosticReport:
        findings: list[str] = []
        recommendations: list[str] = []

        if health.status == HealthStatus.UNHEALTHY:
            findings.append("System health is unhealthy")
            recommendations.append("Inspect unhealthy components and recent errors")
        elif health.status == HealthStatus.DEGRADED:
            findings.append("System health is degraded")
            recommendations.append("Check degraded modules and dependency status")

        for comp in health.components:
            if comp.status in {HealthStatus.UNHEALTHY, HealthStatus.DEGRADED}:
                findings.append(f"Component {comp.name}: {comp.status.value} — {comp.message}")

        error_count = metrics.get("errors_total", 0)
        if error_count > 10:
            findings.append(f"Elevated error count: {error_count}")
            recommendations.append("Review recent error logs and failing modules")

        if not findings:
            findings.append("No critical issues detected")
            recommendations.append("Continue monitoring")

        summary = (
            f"Overall status: {health.status.value}. "
            f"{len(findings)} finding(s)."
        )

        return DiagnosticReport(
            summary=summary,
            findings=findings,
            recommendations=recommendations,
            health=health.to_dict(),
            metrics_snapshot=dict(metrics),
            confidence=0.75,
        )
