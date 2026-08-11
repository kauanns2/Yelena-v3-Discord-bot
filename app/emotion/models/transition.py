"""Transição de estado afetivo."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
import time
import uuid


@dataclass(slots=True)
class Transition:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    from_primary: str = ""
    to_primary: str = ""
    from_valence: float = 0.0
    to_valence: float = 0.0
    magnitude: float = 0.0
    stimulus_id: str | None = None
    cause: str = ""
    correlation_id: str | None = None
    timestamp: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "from_primary": self.from_primary,
            "to_primary": self.to_primary,
            "from_valence": self.from_valence,
            "to_valence": self.to_valence,
            "magnitude": self.magnitude,
            "stimulus_id": self.stimulus_id,
            "cause": self.cause,
            "correlation_id": self.correlation_id,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }
