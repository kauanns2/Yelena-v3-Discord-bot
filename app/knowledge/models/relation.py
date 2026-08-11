"""Relação entre entidades/fatos."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
import time
import uuid

from app.knowledge.constants import RelationType


@dataclass(slots=True)
class Relation:
    source_id: str
    target_id: str
    relation_type: RelationType = RelationType.RELATED_TO
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    weight: float = 1.0
    confidence: float = 0.7
    evidence_ids: list[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.source_id or not self.target_id:
            raise ValueError("Relation requires source_id and target_id")
        self.weight = max(0.0, min(1.0, self.weight))
        self.confidence = max(0.0, min(1.0, self.confidence))

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "relation_type": self.relation_type.value,
            "weight": self.weight,
            "confidence": self.confidence,
            "evidence_ids": list(self.evidence_ids),
            "created_at": self.created_at,
            "metadata": self.metadata,
        }
