"""PersonalityProfile, Trait e Modifier."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
import time
import uuid

from app.personality.constants import DEFAULT_TRAIT_VALUE, ModifierSource


@dataclass(slots=True)
class Trait:
    id: str
    value: float = DEFAULT_TRAIT_VALUE
    baseline: float = DEFAULT_TRAIT_VALUE
    min_value: float = 0.0
    max_value: float = 1.0
    stability: float = 0.8
    confidence: float = 0.8
    source: str = "initial"
    updated_at: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.value = _clamp(self.value, self.min_value, self.max_value)
        self.baseline = _clamp(self.baseline, self.min_value, self.max_value)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "value": self.value,
            "baseline": self.baseline,
            "min_value": self.min_value,
            "max_value": self.max_value,
            "stability": self.stability,
            "confidence": self.confidence,
            "source": self.source,
            "updated_at": self.updated_at,
            "metadata": self.metadata,
        }


@dataclass(slots=True)
class PersonalityModifier:
    trait_id: str
    delta: float
    source: ModifierSource = ModifierSource.TEMPORARY
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    context: str = ""
    duration: float | None = None  # seconds; None = until removed
    priority: int = 50
    confidence: float = 0.7
    created_at: float = field(default_factory=time.time)
    expires_at: float | None = None

    def __post_init__(self) -> None:
        if self.duration is not None and self.expires_at is None:
            self.expires_at = self.created_at + self.duration

    @property
    def is_expired(self) -> bool:
        return self.expires_at is not None and time.time() > self.expires_at

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "trait_id": self.trait_id,
            "delta": self.delta,
            "source": self.source.value,
            "context": self.context,
            "duration": self.duration,
            "priority": self.priority,
            "confidence": self.confidence,
            "created_at": self.created_at,
            "expires_at": self.expires_at,
        }


@dataclass(slots=True)
class PersonalityProfile:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "Yelena"
    version: int = 1
    traits: dict[str, Trait] = field(default_factory=dict)
    values: dict[str, float] = field(default_factory=dict)  # value_id -> priority 0-1
    preferences: list[str] = field(default_factory=list)
    boundaries: list[str] = field(default_factory=list)
    modifiers: list[PersonalityModifier] = field(default_factory=list)
    confidence: float = 0.8
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)

    def get_trait(self, trait_id: str) -> Trait | None:
        return self.traits.get(trait_id)

    def set_trait(self, trait: Trait) -> None:
        self.traits[trait.id] = trait
        self.updated_at = time.time()

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "traits": {k: v.to_dict() for k, v in self.traits.items()},
            "values": dict(self.values),
            "preferences": list(self.preferences),
            "boundaries": list(self.boundaries),
            "modifiers": [m.to_dict() for m in self.modifiers if not m.is_expired],
            "confidence": self.confidence,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "metadata": self.metadata,
        }


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))
