"""Testes do Knowledge Manager."""

import pytest

from app.knowledge import KnowledgeManager
from app.knowledge.constants import KnowledgeStatus, RelationType
from app.knowledge.errors import KnowledgeValidationError, KnowledgeNotFoundError


def test_add_and_query_fact():
    km = KnowledgeManager()
    km.start()
    km.add_fact(
        "Yelena é uma IA modular",
        subject="Yelena",
        predicate="é",
        object="IA modular",
    )
    result = km.query_text("Yelena")
    assert result.total >= 1
    assert any("Yelena" in f.statement for f in result.facts)


def test_empty_statement_fails():
    km = KnowledgeManager()
    with pytest.raises(KnowledgeValidationError):
        km.add_fact("   ")


def test_entity_and_relation():
    km = KnowledgeManager()
    e1 = km.add_entity("Yelena", entity_type="agent")
    e2 = km.add_entity("Kauan", entity_type="user")
    rel = km.add_relation(e1.id, e2.id, RelationType.RELATED_TO)
    assert rel.source_id == e1.id


def test_contradiction():
    km = KnowledgeManager()
    km.add_fact("céu é azul", subject="céu", predicate="é", object="azul")
    f2 = km.add_fact("céu é verde", subject="céu", predicate="é", object="verde")
    assert f2.status == KnowledgeStatus.DISPUTED


def test_invalidate():
    km = KnowledgeManager()
    fact = km.add_fact("dado temporário")
    inv = km.invalidate_fact(fact.id)
    assert inv.status == KnowledgeStatus.INVALIDATED


def test_not_found():
    km = KnowledgeManager()
    with pytest.raises(KnowledgeNotFoundError):
        km.invalidate_fact("missing")
