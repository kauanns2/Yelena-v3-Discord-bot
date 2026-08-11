"""Adapters para Memory, Knowledge e Neural Web."""

from __future__ import annotations

from typing import Any, Protocol

from app.context.constants import ContextItemSource, ContextPriority
from app.context.models.context import ContextItem
from app.context.models.query import ContextQuery


class MemoryAdapterProtocol(Protocol):
    def recall_for_context(self, query: ContextQuery) -> list[ContextItem]: ...


class KnowledgeAdapterProtocol(Protocol):
    def query_for_context(self, query: ContextQuery) -> list[ContextItem]: ...


class NeuralAdapterProtocol(Protocol):
    def related_for_context(self, query: ContextQuery) -> list[ContextItem]: ...


class MemoryContextAdapter:
    """Adapta MemoryManager → ContextItems."""

    def __init__(self, memory_manager: Any = None) -> None:
        self._memory = memory_manager

    def recall_for_context(self, query: ContextQuery) -> list[ContextItem]:
        if self._memory is None or not query.include_memory:
            return []
        if not query.situation:
            return []

        try:
            result = self._memory.recall_text(
                query.situation,
                user_id=query.user_id,
                session_id=query.session_id,
                limit=query.max_items,
            )
        except Exception:
            return []

        items: list[ContextItem] = []
        for mem in result.memories:
            score = result.scores.get(mem.id, 0.5)
            items.append(
                ContextItem(
                    content=mem.content,
                    source=ContextItemSource.MEMORY,
                    source_id=mem.id,
                    relevance=score,
                    priority=ContextPriority.HIGH if mem.importance >= 0.7 else ContextPriority.NORMAL,
                    confidence=mem.confidence,
                    privacy=mem.privacy.value if hasattr(mem.privacy, "value") else str(mem.privacy),
                    tags=list(mem.tags),
                    metadata={"memory_type": mem.memory_type.value},
                )
            )
        return items


class KnowledgeContextAdapter:
    """Adapta KnowledgeManager → ContextItems."""

    def __init__(self, knowledge_manager: Any = None) -> None:
        self._knowledge = knowledge_manager

    def query_for_context(self, query: ContextQuery) -> list[ContextItem]:
        if self._knowledge is None or not query.include_knowledge:
            return []
        if not query.situation:
            return []

        try:
            result = self._knowledge.query_text(query.situation, limit=query.max_items)
        except Exception:
            return []

        items: list[ContextItem] = []
        for fact in result.facts:
            score = result.scores.get(fact.id, 0.5)
            items.append(
                ContextItem(
                    content=fact.statement,
                    source=ContextItemSource.KNOWLEDGE,
                    source_id=fact.id,
                    relevance=score,
                    priority=ContextPriority.NORMAL,
                    confidence=fact.confidence,
                    privacy="internal",
                    metadata={"subject": fact.subject, "predicate": fact.predicate},
                )
            )
        return items


class NeuralContextAdapter:
    """Adapta Neural Web → ContextItems (stub leve)."""

    def __init__(self, neural_manager: Any = None) -> None:
        self._neural = neural_manager

    def related_for_context(self, query: ContextQuery) -> list[ContextItem]:
        if self._neural is None or not query.include_neural:
            return []
        # Integração completa virá com a Teia mais madura
        return []
