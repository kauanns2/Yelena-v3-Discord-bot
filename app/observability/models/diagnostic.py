"""Diagnostic report."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
import time
import uuid


@dataclass(slots=True)
class DiagnosticReport:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    summary: str = ""
    findings: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    health: dict[str, Any] = field(default_factory=dict)
    metrics_snapshot: dict[str, float] = field(default_factory=dict)
    confidence: float = 0.7
    created_at: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "summary": self.summary,
            "findings": list(self.findings),
            "recommendations": list(self.recommendations),
            "health": self.health,
            "metrics_snapshot": self.metrics_snapshot,
            "confidence": self.confidence,
            "created_at": self.created_at,
            "metadata": self.metadata,
        }
