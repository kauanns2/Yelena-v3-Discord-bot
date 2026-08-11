"""Memory Manager — coordenação do sistema de memória."""

from __future__ import annotations

import logging
import time
from typing import Any

from app.memory.constants import (
    MemoryType,
    MemoryStatus,
    PrivacyLevel,
    MemorySource,
    DEFAULT_MAX_RETRIEVAL,
    DEFAULT_WORKING_TTL,
)
from app.memory.errors import MemoryValidationError
from app.memory.models.memory import Memory
from app.memory.models.query import MemoryQuery, MemoryQueryResult
from app.memory.policies import apply_decay, should_forget, should_consolidate, consolidate, forget
from app.memory.retrieval import MemoryRetriever
from app.memory.store import MemoryStore, InMemoryStore
from app.memory.types import MemoryId

logger = logging.getLogger(__name__)


class MemoryManager:
    """API principal do Memory System.

    Registra, recupera, reforça, consolida e esquece memórias.
    Não é Knowledge System.
    """

    def __init__(self, store: MemoryStore | None = None) -> None:
        self._store = store or InMemoryStore()
        self._retriever = MemoryRetriever()
        self._started = False
        self._metrics = {
            "memories_created": 0,
            "memories_recalled": 0,
            "memories_reinforced": 0,
            "memories_consolidated": 0,
            "memories_forgotten": 0,
        }

    @property
    def is_started(self) -> bool:
        return self._started

    def start(self) -> None:
        self._started = True
        logger.info("memory system started", extra={"count": len(self._store)})

    def stop(self) -> None:
        self._started = False
        logger.info("memory system stopped")

    def create(
        self,
        content: str,
        *,
        memory_type: MemoryType = MemoryType.EPISODIC,
        importance: float = 0.5,
        confidence: float = 0.7,
        privacy: PrivacyLevel = PrivacyLevel.PRIVATE,
        source: MemorySource = MemorySource.CONVERSATION,
        user_id: str | None = None,
        session_id: str | None = None,
        tags: list[str] | None = None,
        emotional_valence: float = 0.0,
        ttl: float | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Memory:
        if not content or not content.strip():
            raise MemoryValidationError("Memory content is required")

        expires_at = None
        if ttl is not None:
            expires_at = time.time() + ttl
        elif memory_type == MemoryType.WORKING:
            expires_at = time.time() + DEFAULT_WORKING_TTL

        memory = Memory(
            content=content.strip(),
            memory_type=memory_type,
            importance=importance,
            confidence=confidence,
            privacy=privacy,
            source=source,
            user_id=user_id,
            session_id=session_id,
            tags=tags or [],
            emotional_valence=emotional_valence,
            expires_at=expires_at,
            metadata=metadata or {},
        )
        self._store.save(memory)
        self._metrics["memories_created"] += 1
        logger.debug("memory created", extra={"memory_id": memory.id, "type": memory_type.value})
        return memory

    def get(self, memory_id: MemoryId) -> Memory | None:
        return self._store.get(memory_id)

    def recall(self, query: MemoryQuery) -> MemoryQueryResult:
        if query.limit <= 0:
            query.limit = DEFAULT_MAX_RETRIEVAL

        memories = self._store.list_all()
        # aplicar decay lazy
        for mem in memories:
            apply_decay(mem)

        result = self._retriever.retrieve(memories, query)
        self._metrics["memories_recalled"] += len(result.memories)
        return result

    def recall_text(
        self,
        text: str,
        *,
        user_id: str | None = None,
        session_id: str | None = None,
        limit: int = DEFAULT_MAX_RETRIEVAL,
    ) -> MemoryQueryResult:
        query = MemoryQuery(
            text=text,
            user_id=user_id,
            session_id=session_id,
            limit=limit,
        )
        return self.recall(query)

    def reinforce(self, memory_id: MemoryId, amount: float = 0.1) -> Memory:
        mem = self._store.get(memory_id)
        if mem is None:
            from app.memory.errors import MemoryNotFoundError

            raise MemoryNotFoundError(f"Memory not found: {memory_id}")
        mem.reinforce(amount)
        self._store.save(mem)
        self._metrics["memories_reinforced"] += 1
        return mem

    def consolidate(self, memory_id: MemoryId) -> Memory:
        mem = self._store.get(memory_id)
        if mem is None:
            from app.memory.errors import MemoryNotFoundError

            raise MemoryNotFoundError(f"Memory not found: {memory_id}")
        consolidate(mem)
        self._store.save(mem)
        self._metrics["memories_consolidated"] += 1
        return mem

    def forget(self, memory_id: MemoryId) -> Memory:
        mem = self._store.get(memory_id)
        if mem is None:
            from app.memory.errors import MemoryNotFoundError

            raise MemoryNotFoundError(f"Memory not found: {memory_id}")
        forget(mem)
        self._store.save(mem)
        self._metrics["memories_forgotten"] += 1
        return mem

    def maintenance(self) -> dict[str, int]:
        """Aplica decay/consolidação/esquecimento em lote."""
        consolidated = 0
        forgotten = 0
        for mem in self._store.list_all():
            apply_decay(mem)
            if should_consolidate(mem):
                consolidate(mem)
                consolidated += 1
            if should_forget(mem):
                forget(mem)
                forgotten += 1
            self._store.save(mem)
        self._metrics["memories_consolidated"] += consolidated
        self._metrics["memories_forgotten"] += forgotten
        return {"consolidated": consolidated, "forgotten": forgotten}

    def health(self) -> dict[str, Any]:
        return {
            "status": "healthy" if self._started else "stopped",
            "count": len(self._store),
            "metrics": dict(self._metrics),
        }
