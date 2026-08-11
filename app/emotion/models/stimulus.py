"""Estímulo afetivo."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
import time
import uuid

from app.emotion.constants import StimulusType


@dataclass(slots=True)
class Stimulus:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    stimulus_type: StimulusType = StimulusType.CONVERSATION
    source: str = ""
    intensity: float = 0.5
    valence: float = 0.0
    target: str | None = None
    context: dict[str, Any] = field(default_factory=dict)
    correlation_id: str | None = None
    timestamp: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.intensity = max(0.0, min(1.0, self.intensity))
        self.valence = max(-1.0, min(1.0, self.valence))

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "stimulus_type": self.stimulus_type.value,
            "source": self.source,
            "intensity": self.intensity,
            "valence": self.valence,
            "target": self.target,
            "context": self.context,
            "correlation_id": self.correlation_id,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }
