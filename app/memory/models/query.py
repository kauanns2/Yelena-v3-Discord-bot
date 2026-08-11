"""Query e resultado de recuperação de memórias."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.memory.constants import MemoryType, PrivacyLevel
from app.memory.models.memory import Memory


@dataclass(slots=True)
class MemoryQuery:
    text: str = ""
    memory_types: list[MemoryType] | None = None
    user_id: str | None = None
    session_id: str | None = None
    tags: list[str] | None = None
    min_importance: float = 0.0
    min_confidence: float = 0.0
    max_privacy: PrivacyLevel | None = None
    limit: int = 20
    include_forgotten: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class MemoryQueryResult:
    memories: list[Memory] = field(default_factory=list)
    total: int = 0
    query: MemoryQuery | None = None
    scores: dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "memories": [m.to_dict() for m in self.memories],
            "total": self.total,
            "scores": self.scores,
        }
