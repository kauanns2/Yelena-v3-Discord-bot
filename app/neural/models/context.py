"""Contexto de propagação na Teia."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
import time


@dataclass(slots=True)
class NeuralContext:
    """Contexto leve associado a uma propagação."""

    session_id: str | None = None
    correlation_id: str | None = None
    trace_id: str | None = None
    user_id: str | None = None
    intent: str | None = None
    priority: int = 50
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "correlation_id": self.correlation_id,
            "trace_id": self.trace_id,
            "user_id": self.user_id,
            "intent": self.intent,
            "priority": self.priority,
            "metadata": self.metadata,
            "created_at": self.created_at,
        }
