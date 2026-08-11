"""Detecção básica de contradições."""

from __future__ import annotations

from app.knowledge.constants import KnowledgeStatus
from app.knowledge.models.fact import Fact


def find_contradicting_facts(new_fact: Fact, existing: list[Fact]) -> list[Fact]:
    """Heurística simples: mesmo subject+predicate com object diferente."""
    contradictions: list[Fact] = []
    if not new_fact.subject or not new_fact.predicate:
        return contradictions

    for fact in existing:
        if not fact.is_valid:
            continue
        if fact.id == new_fact.id:
            continue
        if (
            fact.subject.lower() == new_fact.subject.lower()
            and fact.predicate.lower() == new_fact.predicate.lower()
            and fact.object
            and new_fact.object
            and fact.object.lower() != new_fact.object.lower()
        ):
            contradictions.append(fact)
    return contradictions


def mark_disputed(facts: list[Fact]) -> None:
    for fact in facts:
        fact.status = KnowledgeStatus.DISPUTED
