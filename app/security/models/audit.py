"""Audit record."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
import time
import uuid


@dataclass(slots=True)
class AuditRecord:
    event: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    identity_id: str = ""
    resource: str = ""
    action: str = ""
    effect: str = ""
    reason: str = ""
    correlation_id: str | None = None
    timestamp: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "event": self.event,
            "identity_id": self.identity_id,
            "resource": self.resource,
            "action": self.action,
            "effect": self.effect,
            "reason": self.reason,
            "correlation_id": self.correlation_id,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }
