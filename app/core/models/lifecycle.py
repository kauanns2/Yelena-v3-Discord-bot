"""Eventos de lifecycle."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
import time

from app.core.constants import LifecycleState


@dataclass(slots=True)
class LifecycleEvent:
    """Evento de mudança de lifecycle."""

    source: str
    from_state: LifecycleState
    to_state: LifecycleState
    timestamp: float = field(default_factory=time.time)
    reason: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "from_state": self.from_state.value,
            "to_state": self.to_state.value,
            "timestamp": self.timestamp,
            "reason": self.reason,
            "metadata": self.metadata,
        }
