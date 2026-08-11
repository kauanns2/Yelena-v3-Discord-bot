"""Alert model."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
import time
import uuid

from app.observability.constants import AlertSeverity


@dataclass(slots=True)
class Alert:
    title: str
    severity: AlertSeverity = AlertSeverity.WARNING
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    message: str = ""
    source: str = ""
    fingerprint: str = ""
    active: bool = True
    created_at: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "severity": self.severity.value,
            "message": self.message,
            "source": self.source,
            "fingerprint": self.fingerprint,
            "active": self.active,
            "created_at": self.created_at,
            "metadata": self.metadata,
        }
