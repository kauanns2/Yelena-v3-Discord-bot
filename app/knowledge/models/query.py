"""Query de conhecimento."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.knowledge.models.fact import Fact
from app.knowledge.models.entity import Entity
from app.knowledge.models.relation import Relation


@dataclass(slots=True)
class KnowledgeQuery:
    text: str = ""
    subject: str | None = None
    predicate: str | None = None
    object: str | None = None
    min_confidence: float = 0.0
    only_valid: bool = True
    limit: int = 20
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class KnowledgeQueryResult:
    facts: list[Fact] = field(default_factory=list)
    entities: list[Entity] = field(default_factory=list)
    relations: list[Relation] = field(default_factory=list)
    total: int = 0
    scores: dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "facts": [f.to_dict() for f in self.facts],
            "entities": [e.to_dict() for e in self.entities],
            "relations": [r.to_dict() for r in self.relations],
            "total": self.total,
            "scores": self.scores,
        }
