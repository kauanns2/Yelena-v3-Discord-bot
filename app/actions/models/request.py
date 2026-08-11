"""ActionRequest."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
import time
import uuid

from app.actions.constants import RiskLevel


@dataclass(slots=True)
class ActionRequest:
    tool_id: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    arguments: dict[str, Any] = field(default_factory=dict)
    dry_run: bool = False
    requested_by: str = ""
    session_id: str | None = None
    correlation_id: str | None = None
    risk_hint: RiskLevel | None = None
    requires_confirmation: bool = False
    confirmed: bool = False
    timeout: float | None = None
    created_at: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "tool_id": self.tool_id,
            "arguments": self.arguments,
            "dry_run": self.dry_run,
            "requested_by": self.requested_by,
            "session_id": self.session_id,
            "correlation_id": self.correlation_id,
            "risk_hint": self.risk_hint.value if self.risk_hint else None,
            "requires_confirmation": self.requires_confirmation,
            "confirmed": self.confirmed,
            "timeout": self.timeout,
            "created_at": self.created_at,
            "metadata": self.metadata,
        }
