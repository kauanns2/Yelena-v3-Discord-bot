"""Modelo central de memória."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
import time
import uuid

from app.memory.constants import (
    MemoryType,
    MemoryStatus,
    PrivacyLevel,
    MemorySource,
    DEFAULT_IMPORTANCE,
    DEFAULT_CONFIDENCE,
    DEFAULT_STRENGTH,
    DEFAULT_DECAY_RATE,
)


@dataclass(slots=True)
class Memory:
    content: str
    memory_type: MemoryType = MemoryType.EPISODIC
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    summary: str = ""
    importance: float = DEFAULT_IMPORTANCE
    confidence: float = DEFAULT_CONFIDENCE
    strength: float = DEFAULT_STRENGTH
    decay_rate: float = DEFAULT_DECAY_RATE
    status: MemoryStatus = MemoryStatus.ACTIVE
    privacy: PrivacyLevel = PrivacyLevel.PRIVATE
    source: MemorySource = MemorySource.CONVERSATION
    user_id: str | None = None
    session_id: str | None = None
    tags: list[str] = field(default_factory=list)
    associations: list[str] = field(default_factory=list)  # other memory ids
    emotional_valence: float = 0.0  # -1.0 to 1.0
    access_count: int = 0
    last_accessed_at: float | None = None
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    expires_at: float | None = None
    version: int = 1
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.content or not self.content.strip():
            raise ValueError("Memory content is required")
        self.importance = _clamp(self.importance)
        self.confidence = _clamp(self.confidence)
        self.strength = max(0.0, self.strength)
        self.emotional_valence = max(-1.0, min(1.0, self.emotional_valence))

    @property
    def is_active(self) -> bool:
        return self.status in {MemoryStatus.ACTIVE, MemoryStatus.CONSOLIDATED, MemoryStatus.DECAYING}

    @property
    def is_expired(self) -> bool:
        return self.expires_at is not None and time.time() > self.expires_at

    def reinforce(self, amount: float = 0.1) -> None:
        self.strength = min(2.0, self.strength + amount)
        self.importance = _clamp(self.importance + amount * 0.5)
        self.access_count += 1
        self.last_accessed_at = time.time()
        self.updated_at = time.time()
        self.version += 1

    def decay(self, dt_seconds: float = 1.0) -> None:
        factor = max(0.0, 1.0 - self.decay_rate * (dt_seconds / 3600.0))
        self.strength *= factor
        if self.strength < 0.05:
            self.status = MemoryStatus.DECAYING
        self.updated_at = time.time()

    def touch(self) -> None:
        self.access_count += 1
        self.last_accessed_at = time.time()

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "content": self.content,
            "summary": self.summary,
            "memory_type": self.memory_type.value,
            "importance": self.importance,
            "confidence": self.confidence,
            "strength": self.strength,
            "status": self.status.value,
            "privacy": self.privacy.value,
            "source": self.source.value,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "tags": list(self.tags),
            "associations": list(self.associations),
            "emotional_valence": self.emotional_valence,
            "access_count": self.access_count,
            "last_accessed_at": self.last_accessed_at,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "expires_at": self.expires_at,
            "version": self.version,
            "metadata": self.metadata,
        }


def _clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, value))
