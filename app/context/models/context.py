"""CognitiveContext e ContextItem."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
import time
import uuid

from app.context.constants import ContextItemSource, ContextPriority


@dataclass(slots=True)
class ContextItem:
    content: str
    source: ContextItemSource
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source_id: str | None = None  # id na origem (memory_id, fact_id, etc.)
    relevance: float = 0.5
    priority: ContextPriority = ContextPriority.NORMAL
    confidence: float = 0.7
    token_estimate: int = 0
    privacy: str = "private"
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.relevance = max(0.0, min(1.0, self.relevance))
        self.confidence = max(0.0, min(1.0, self.confidence))
        if self.token_estimate <= 0 and self.content:
            # estimativa simples: ~4 chars por token
            self.token_estimate = max(1, len(self.content) // 4)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "content": self.content,
            "source": self.source.value,
            "source_id": self.source_id,
            "relevance": self.relevance,
            "priority": self.priority.value,
            "confidence": self.confidence,
            "token_estimate": self.token_estimate,
            "privacy": self.privacy,
            "tags": list(self.tags),
            "metadata": self.metadata,
        }


@dataclass(slots=True)
class CognitiveContext:
    """Contexto cognitivo montado para uma situação."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str | None = None
    user_id: str | None = None
    situation: str = ""
    items: list[ContextItem] = field(default_factory=list)
    token_budget: int = 2000
    tokens_used: int = 0
    correlation_id: str | None = None
    created_at: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def item_count(self) -> int:
        return len(self.items)

    def summary_texts(self) -> list[str]:
        return [i.content for i in self.items]

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "session_id": self.session_id,
            "user_id": self.user_id,
            "situation": self.situation,
            "items": [i.to_dict() for i in self.items],
            "token_budget": self.token_budget,
            "tokens_used": self.tokens_used,
            "item_count": self.item_count,
            "correlation_id": self.correlation_id,
            "created_at": self.created_at,
            "metadata": self.metadata,
        }
