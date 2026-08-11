"""Knowledge Manager."""

from __future__ import annotations

import logging
import time
from typing import Any

from app.knowledge.constants import KnowledgeStatus, RelationType, DEFAULT_MAX_RETRIEVAL
from app.knowledge.contradiction import find_contradicting_facts, mark_disputed
from app.knowledge.errors import KnowledgeValidationError, KnowledgeNotFoundError
from app.knowledge.models.fact import Fact
from app.knowledge.models.entity import Entity
from app.knowledge.models.relation import Relation
from app.knowledge.models.assertion import Assertion
from app.knowledge.models.query import KnowledgeQuery, KnowledgeQueryResult
from app.knowledge.retrieval import KnowledgeRetriever
from app.knowledge.store import KnowledgeStore
from app.knowledge.types import KnowledgeId

logger = logging.getLogger(__name__)


class KnowledgeManager:
    """API principal do Knowledge System.

    Knowledge ≠ Memory.
    """

    def __init__(self) -> None:
        self._store = KnowledgeStore()
        self._retriever = KnowledgeRetriever()
        self._started = False
        self._metrics = {
            "facts_created": 0,
            "entities_created": 0,
            "relations_created": 0,
            "queries": 0,
            "contradictions": 0,
        }

    @property
    def is_started(self) -> bool:
        return self._started

    def start(self) -> None:
        self._started = True
        logger.info("knowledge system started", extra=self._store.stats())

    def stop(self) -> None:
        self._started = False

    def add_fact(
        self,
        statement: str,
        *,
        subject: str = "",
        predicate: str = "",
        object: str = "",
        confidence: float = 0.7,
        evidence_ids: list[str] | None = None,
        source: str = "",
        check_contradictions: bool = True,
        metadata: dict[str, Any] | None = None,
    ) -> Fact:
        if not statement or not statement.strip():
            raise KnowledgeValidationError("Fact statement is required")

        fact = Fact(
            statement=statement.strip(),
            subject=subject,
            predicate=predicate,
            object=object,
            confidence=confidence,
            evidence_ids=evidence_ids or [],
            source=source,
            metadata=metadata or {},
        )

        if check_contradictions:
            existing = list(self._store.facts.values())
            contradictions = find_contradicting_facts(fact, existing)
            if contradictions:
                mark_disputed([fact] + contradictions)
                self._metrics["contradictions"] += 1
                for c in contradictions:
                    self._store.save_fact(c)

        self._store.save_fact(fact)
        self._metrics["facts_created"] += 1
        return fact

    def add_entity(
        self,
        name: str,
        *,
        entity_type: str = "generic",
        aliases: list[str] | None = None,
        attributes: dict[str, Any] | None = None,
        confidence: float = 0.7,
    ) -> Entity:
        entity = Entity(
            name=name,
            entity_type=entity_type,
            aliases=aliases or [],
            attributes=attributes or {},
            confidence=confidence,
        )
        self._store.save_entity(entity)
        self._metrics["entities_created"] += 1
        return entity

    def add_relation(
        self,
        source_id: str,
        target_id: str,
        relation_type: RelationType = RelationType.RELATED_TO,
        *,
        weight: float = 1.0,
        confidence: float = 0.7,
        evidence_ids: list[str] | None = None,
    ) -> Relation:
        relation = Relation(
            source_id=source_id,
            target_id=target_id,
            relation_type=relation_type,
            weight=weight,
            confidence=confidence,
            evidence_ids=evidence_ids or [],
        )
        self._store.save_relation(relation)
        self._metrics["relations_created"] += 1
        return relation

    def add_assertion(
        self,
        claim: str,
        *,
        confidence: float = 0.7,
        supports: list[str] | None = None,
        source: str = "",
    ) -> Assertion:
        assertion = Assertion(
            claim=claim,
            confidence=confidence,
            supports=supports or [],
            source=source,
        )
        self._store.save_assertion(assertion)
        return assertion

    def get_fact(self, fact_id: KnowledgeId) -> Fact | None:
        return self._store.get_fact(fact_id)

    def query(self, query: KnowledgeQuery) -> KnowledgeQueryResult:
        if query.limit <= 0:
            query.limit = DEFAULT_MAX_RETRIEVAL
        result = self._retriever.retrieve(self._store, query)
        self._metrics["queries"] += 1
        return result

    def query_text(self, text: str, limit: int = DEFAULT_MAX_RETRIEVAL) -> KnowledgeQueryResult:
        return self.query(KnowledgeQuery(text=text, limit=limit))

    def invalidate_fact(self, fact_id: KnowledgeId) -> Fact:
        fact = self._store.get_fact(fact_id)
        if fact is None:
            raise KnowledgeNotFoundError(f"Fact not found: {fact_id}")
        fact.status = KnowledgeStatus.INVALIDATED
        fact.updated_at = time.time()
        fact.version += 1
        self._store.save_fact(fact)
        return fact

    def health(self) -> dict[str, Any]:
        return {
            "status": "healthy" if self._started else "stopped",
            **self._store.stats(),
            "metrics": dict(self._metrics),
        }
