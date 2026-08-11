"""Recuperação de conhecimento."""

from __future__ import annotations

import re

from app.knowledge.models.fact import Fact
from app.knowledge.models.query import KnowledgeQuery, KnowledgeQueryResult
from app.knowledge.store import KnowledgeStore


class KnowledgeRetriever:
    def retrieve(self, store: KnowledgeStore, query: KnowledgeQuery) -> KnowledgeQueryResult:
        scored: list[tuple[Fact, float]] = []

        for fact in store.facts.values():
            if query.only_valid and not fact.is_valid:
                continue
            if fact.confidence < query.min_confidence:
                continue
            if query.subject and query.subject.lower() not in fact.subject.lower() and query.subject.lower() not in fact.statement.lower():
                if query.predicate or query.object:
                    pass  # still check other fields
                elif not query.text:
                    continue
            if query.predicate and query.predicate.lower() not in fact.predicate.lower():
                if not query.text:
                    continue
            if query.object and query.object.lower() not in fact.object.lower():
                if not query.text:
                    continue

            score = self._score_fact(fact, query)
            if score > 0:
                scored.append((fact, score))

        scored.sort(key=lambda x: x[1], reverse=True)
        limited = scored[: query.limit]

        facts = [f for f, _ in limited]
        scores = {f.id: s for f, s in limited}

        # entidades simples por nome
        entities = []
        if query.text:
            text = query.text.lower()
            for ent in store.entities.values():
                if text in ent.name.lower() or any(text in a.lower() for a in ent.aliases):
                    entities.append(ent)

        return KnowledgeQueryResult(
            facts=facts,
            entities=entities[: query.limit],
            total=len(scored),
            scores=scores,
        )

    def _score_fact(self, fact: Fact, query: KnowledgeQuery) -> float:
        score = 0.0
        if query.text:
            text = query.text.lower()
            statement = fact.statement.lower()
            if text in statement:
                score += 0.5
            else:
                tokens = set(re.findall(r"\w+", text))
                st_tokens = set(re.findall(r"\w+", statement))
                if tokens:
                    score += (len(tokens & st_tokens) / len(tokens)) * 0.4
        else:
            score += 0.2

        if query.subject and query.subject.lower() in fact.subject.lower():
            score += 0.2
        if query.predicate and query.predicate.lower() in fact.predicate.lower():
            score += 0.15
        if query.object and query.object.lower() in fact.object.lower():
            score += 0.15

        score += fact.confidence * 0.2
        return score
