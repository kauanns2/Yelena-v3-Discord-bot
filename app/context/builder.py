"""Context Builder — ranking, budget, dedup, compressão."""

from __future__ import annotations

from app.context.constants import DEFAULT_TOKEN_BUDGET, DEFAULT_MIN_RELEVANCE
from app.context.models.context import CognitiveContext, ContextItem
from app.context.models.query import ContextQuery


class ContextBuilder:
    """Monta CognitiveContext a partir de itens candidatos."""

    def build(
        self,
        query: ContextQuery,
        candidates: list[ContextItem],
    ) -> CognitiveContext:
        # filtrar relevância mínima
        filtered = [c for c in candidates if c.relevance >= query.min_relevance]

        # deduplicar por conteúdo similar
        filtered = self._deduplicate(filtered)

        # rankear
        filtered.sort(
            key=lambda x: (x.priority.value, x.relevance, x.confidence),
            reverse=True,
        )

        # aplicar budget de tokens e max_items
        selected: list[ContextItem] = []
        tokens_used = 0
        budget = query.token_budget or DEFAULT_TOKEN_BUDGET

        for item in filtered:
            if len(selected) >= query.max_items:
                break
            if tokens_used + item.token_estimate > budget:
                continue
            selected.append(item)
            tokens_used += item.token_estimate

        return CognitiveContext(
            session_id=query.session_id,
            user_id=query.user_id,
            situation=query.situation,
            items=selected,
            token_budget=budget,
            tokens_used=tokens_used,
            correlation_id=query.correlation_id,
            metadata={
                "candidates": len(candidates),
                "filtered": len(filtered),
                "selected": len(selected),
            },
        )

    def _deduplicate(self, items: list[ContextItem]) -> list[ContextItem]:
        seen: set[str] = set()
        result: list[ContextItem] = []
        for item in items:
            key = item.content.strip().lower()[:200]
            if key in seen:
                continue
            seen.add(key)
            result.append(item)
        return result
