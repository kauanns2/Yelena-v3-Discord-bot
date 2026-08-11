"""Estado afetivo e vetor emocional."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
import time
import uuid

from app.emotion.constants import (
    EmotionLabel,
    DEFAULT_VALENCE,
    DEFAULT_AROUSAL,
    DEFAULT_DOMINANCE,
    DEFAULT_INTENSITY,
    DEFAULT_STABILITY,
)


@dataclass(slots=True)
class EmotionVector:
    """Mistura de emoções com pesos 0.0–1.0."""

    weights: dict[str, float] = field(default_factory=dict)

    def set(self, label: str | EmotionLabel, value: float) -> None:
        key = label.value if isinstance(label, EmotionLabel) else label
        self.weights[key] = max(0.0, min(1.0, value))

    def get(self, label: str | EmotionLabel) -> float:
        key = label.value if isinstance(label, EmotionLabel) else label
        return self.weights.get(key, 0.0)

    def primary(self) -> str:
        if not self.weights:
            return EmotionLabel.NEUTRAL.value
        return max(self.weights, key=self.weights.get)  # type: ignore[arg-type]

    def secondary(self, n: int = 2) -> list[str]:
        ordered = sorted(self.weights.items(), key=lambda x: x[1], reverse=True)
        primary = self.primary()
        return [k for k, v in ordered if k != primary and v > 0][:n]

    def to_dict(self) -> dict[str, float]:
        return dict(self.weights)


@dataclass(slots=True)
class AffectiveState:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    primary_emotion: str = EmotionLabel.NEUTRAL.value
    secondary_emotions: list[str] = field(default_factory=list)
    vector: EmotionVector = field(default_factory=EmotionVector)
    valence: float = DEFAULT_VALENCE
    arousal: float = DEFAULT_AROUSAL
    dominance: float = DEFAULT_DOMINANCE
    intensity: float = DEFAULT_INTENSITY
    stability: float = DEFAULT_STABILITY
    confidence: float = 0.7
    source: str = "baseline"
    triggers: list[str] = field(default_factory=list)
    # internal complementary signals
    energy: float = 0.7
    fatigue: float = 0.2
    stress: float = 0.1
    ph: float | None = None  # interface only
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    expires_at: float | None = None
    version: int = 1
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.valence = max(-1.0, min(1.0, self.valence))
        self.arousal = _clamp01(self.arousal)
        self.dominance = _clamp01(self.dominance)
        self.intensity = _clamp01(self.intensity)
        self.stability = _clamp01(self.stability)
        self.confidence = _clamp01(self.confidence)
        self.energy = _clamp01(self.energy)
        self.fatigue = _clamp01(self.fatigue)
        self.stress = _clamp01(self.stress)

    def sync_primary_from_vector(self) -> None:
        self.primary_emotion = self.vector.primary()
        self.secondary_emotions = self.vector.secondary()

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "primary_emotion": self.primary_emotion,
            "secondary_emotions": list(self.secondary_emotions),
            "vector": self.vector.to_dict(),
            "valence": self.valence,
            "arousal": self.arousal,
            "dominance": self.dominance,
            "intensity": self.intensity,
            "stability": self.stability,
            "confidence": self.confidence,
            "source": self.source,
            "triggers": list(self.triggers),
            "energy": self.energy,
            "fatigue": self.fatigue,
            "stress": self.stress,
            "ph": self.ph,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "version": self.version,
            "metadata": self.metadata,
        }


def _clamp01(v: float) -> float:
    return max(0.0, min(1.0, v))
