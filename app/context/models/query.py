"""Query para construção de contexto."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.context.constants import DEFAULT_TOKEN_BUDGET, DEFAULT_MAX_ITEMS, DEFAULT_MIN_RELEVANCE


@dataclass(slots=True)
class ContextQuery:
    situation: str = ""
    session_id: str | None = None
    user_id: str | None = None
    intent: str | None = None
    token_budget: int = DEFAULT_TOKEN_BUDGET
    max_items: int = DEFAULT_MAX_ITEMS
    min_relevance: float = DEFAULT_MIN_RELEVANCE
    include_memory: bool = True
    include_knowledge: bool = True
    include_neural: bool = False
    correlation_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
