"""ActionResult."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
import time
import uuid

from app.actions.constants import ActionStatus, RiskLevel


@dataclass(slots=True)
class ActionResult:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    request_id: str = ""
    tool_id: str = ""
    status: ActionStatus = ActionStatus.PENDING
    success: bool = False
    output: Any = None
    error: str | None = None
    risk: RiskLevel = RiskLevel.LOW
    dry_run: bool = False
    duration_ms: float = 0.0
    correlation_id: str | None = None
    created_at: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "request_id": self.request_id,
            "tool_id": self.tool_id,
            "status": self.status.value,
            "success": self.success,
            "output": self.output,
            "error": self.error,
            "risk": self.risk.value,
            "dry_run": self.dry_run,
            "duration_ms": self.duration_ms,
            "correlation_id": self.correlation_id,
            "created_at": self.created_at,
            "metadata": self.metadata,
        }
