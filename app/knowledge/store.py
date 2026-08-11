"""Store de conhecimento em memória."""

from __future__ import annotations

from app.knowledge.models.fact import Fact
from app.knowledge.models.entity import Entity
from app.knowledge.models.relation import Relation
from app.knowledge.models.assertion import Assertion
from app.knowledge.types import KnowledgeId


class KnowledgeStore:
    def __init__(self) -> None:
        self.facts: dict[KnowledgeId, Fact] = {}
        self.entities: dict[KnowledgeId, Entity] = {}
        self.relations: dict[KnowledgeId, Relation] = {}
        self.assertions: dict[KnowledgeId, Assertion] = {}

    def save_fact(self, fact: Fact) -> Fact:
        self.facts[fact.id] = fact
        return fact

    def save_entity(self, entity: Entity) -> Entity:
        self.entities[entity.id] = entity
        return entity

    def save_relation(self, relation: Relation) -> Relation:
        self.relations[relation.id] = relation
        return relation

    def save_assertion(self, assertion: Assertion) -> Assertion:
        self.assertions[assertion.id] = assertion
        return assertion

    def get_fact(self, fact_id: KnowledgeId) -> Fact | None:
        return self.facts.get(fact_id)

    def get_entity(self, entity_id: KnowledgeId) -> Entity | None:
        return self.entities.get(entity_id)

    def stats(self) -> dict[str, int]:
        return {
            "facts": len(self.facts),
            "entities": len(self.entities),
            "relations": len(self.relations),
            "assertions": len(self.assertions),
        }
