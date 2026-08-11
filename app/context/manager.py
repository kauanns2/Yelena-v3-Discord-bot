"""Context Manager — orquestra construção de contexto cognitivo."""

from __future__ import annotations

import logging
from typing import Any

from app.context.adapters import (
    MemoryContextAdapter,
    KnowledgeContextAdapter,
    NeuralContextAdapter,
)
from app.context.builder import ContextBuilder
from app.context.models.context import CognitiveContext, ContextItem
from app.context.models.query import ContextQuery
from app.context.constants import ContextItemSource, ContextPriority

logger = logging.getLogger(__name__)


class ContextManager:
    """Monta contexto cognitivo seletivo a partir de Memory, Knowledge e outros.

    Fluxo:
    Situation → collect candidates → rank → budget → CognitiveContext
    """

    def __init__(
        self,
        memory_manager: Any = None,
        knowledge_manager: Any = None,
        neural_manager: Any = None,
    ) -> None:
        self._memory_adapter = MemoryContextAdapter(memory_manager)
        self._knowledge_adapter = KnowledgeContextAdapter(knowledge_manager)
        self._neural_adapter = NeuralContextAdapter(neural_manager)
        self._builder = ContextBuilder()
        self._started = False
        self._metrics = {
            "contexts_built": 0,
            "items_collected": 0,
            "items_selected": 0,
        }

    @property
    def is_started(self) -> bool:
        return self._started

    def start(self) -> None:
        self._started = True
        logger.info("context system started")

    def stop(self) -> None:
        self._started = False

    def set_memory_manager(self, manager: Any) -> None:
        self._memory_adapter = MemoryContextAdapter(manager)

    def set_knowledge_manager(self, manager: Any) -> None:
        self._knowledge_adapter = KnowledgeContextAdapter(manager)

    def set_neural_manager(self, manager: Any) -> None:
        self._neural_adapter = NeuralContextAdapter(manager)

    def build(self, query: ContextQuery) -> CognitiveContext:
        candidates: list[ContextItem] = []

        # situação atual como item de sistema
        if query.situation:
            candidates.append(
                ContextItem(
                    content=query.situation,
                    source=ContextItemSource.SYSTEM,
                    relevance=1.0,
                    priority=ContextPriority.CRITICAL,
                    confidence=1.0,
                    tags=["situation"],
                )
            )

        candidates.extend(self._memory_adapter.recall_for_context(query))
        candidates.extend(self._knowledge_adapter.query_for_context(query))
        candidates.extend(self._neural_adapter.related_for_context(query))

        self._metrics["items_collected"] += len(candidates)

        context = self._builder.build(query, candidates)
        self._metrics["contexts_built"] += 1
        self._metrics["items_selected"] += context.item_count

        logger.debug(
            "context built",
            extra={
                "items": context.item_count,
                "tokens": context.tokens_used,
                "budget": context.token_budget,
            },
        )
        return context

    def build_from_text(
        self,
        situation: str,
        *,
        session_id: str | None = None,
        user_id: str | None = None,
        token_budget: int = 2000,
    ) -> CognitiveContext:
        query = ContextQuery(
            situation=situation,
            session_id=session_id,
            user_id=user_id,
            token_budget=token_budget,
        )
        return self.build(query)

    def health(self) -> dict[str, Any]:
        return {
            "status": "healthy" if self._started else "stopped",
            "metrics": dict(self._metrics),
        }
