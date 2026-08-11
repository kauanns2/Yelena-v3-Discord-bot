"""Communication e Social style."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class CommunicationStyle:
    verbosity: float = 0.5
    formality: float = 0.4
    directness: float = 0.6
    humor: float = 0.5
    warmth: float = 0.6
    technicality: float = 0.4
    emotional_expression: float = 0.5
    initiative: float = 0.5
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "verbosity": self.verbosity,
            "formality": self.formality,
            "directness": self.directness,
            "humor": self.humor,
            "warmth": self.warmth,
            "technicality": self.technicality,
            "emotional_expression": self.emotional_expression,
            "initiative": self.initiative,
            "metadata": self.metadata,
        }


@dataclass(slots=True)
class SocialStyle:
    sociability: float = 0.6
    assertiveness: float = 0.5
    cooperation: float = 0.6
    patience: float = 0.6
    responsiveness: float = 0.7
    boundaries: float = 0.7
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "sociability": self.sociability,
            "assertiveness": self.assertiveness,
            "cooperation": self.cooperation,
            "patience": self.patience,
            "responsiveness": self.responsiveness,
            "boundaries": self.boundaries,
            "metadata": self.metadata,
        }
