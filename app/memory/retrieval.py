"""Recuperação e ranking de memórias."""

from __future__ import annotations

import re
from typing import Iterable

from app.memory.constants import MemoryStatus, PrivacyLevel
from app.memory.models.memory import Memory
from app.memory.models.query import MemoryQuery, MemoryQueryResult

PRIVACY_ORDER = {
    PrivacyLevel.PUBLIC: 0,
    PrivacyLevel.INTERNAL: 1,
    PrivacyLevel.PRIVATE: 2,
    PrivacyLevel.SENSITIVE: 3,
    PrivacyLevel.RESTRICTED: 4,
}


class MemoryRetriever:
    """Filtra e ranqueia memórias por relevância."""

    def retrieve(self, memories: Iterable[Memory], query: MemoryQuery) -> MemoryQueryResult:
        candidates: list[tuple[Memory, float]] = []

        for mem in memories:
            if not self._passes_filters(mem, query):
                continue
            score = self._score(mem, query)
            if score > 0:
                candidates.append((mem, score))

        candidates.sort(key=lambda x: x[1], reverse=True)
        limited = candidates[: query.limit]

        result_memories = []
        scores: dict[str, float] = {}
        for mem, score in limited:
            mem.touch()
            result_memories.append(mem)
            scores[mem.id] = score

        return MemoryQueryResult(
            memories=result_memories,
            total=len(candidates),
            query=query,
            scores=scores,
        )

    def _passes_filters(self, mem: Memory, query: MemoryQuery) -> bool:
        if not query.include_forgotten and mem.status == MemoryStatus.FORGOTTEN:
            return False
        if mem.is_expired:
            return False
        if query.memory_types and mem.memory_type not in query.memory_types:
            return False
        if query.user_id and mem.user_id and mem.user_id != query.user_id:
            return False
        if query.session_id and mem.session_id and mem.session_id != query.session_id:
            return False
        if query.tags and not any(t in mem.tags for t in query.tags):
            return False
        if mem.importance < query.min_importance:
            return False
        if mem.confidence < query.min_confidence:
            return False
        if query.max_privacy is not None:
            if PRIVACY_ORDER.get(mem.privacy, 99) > PRIVACY_ORDER.get(query.max_privacy, 99):
                return False
        return True

    def _score(self, mem: Memory, query: MemoryQuery) -> float:
        score = 0.0

        # relevância textual simples
        if query.text:
            text = query.text.lower()
            content = mem.content.lower()
            summary = (mem.summary or "").lower()
            if text in content or text in summary:
                score += 0.5
            else:
                tokens = set(re.findall(r"\w+", text))
                content_tokens = set(re.findall(r"\w+", content))
                if tokens:
                    overlap = len(tokens & content_tokens) / len(tokens)
                    score += overlap * 0.4
        else:
            score += 0.2  # sem texto: base neutra

        score += mem.importance * 0.3
        score += mem.confidence * 0.1
        score += min(mem.strength, 1.0) * 0.15
        score += min(mem.access_count / 10.0, 0.1)

        return score
