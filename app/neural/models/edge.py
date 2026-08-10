"""Aresta / relação entre nós."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
import time
import uuid

from app.neural.constants import EdgeType


@dataclass(slots=True)
class Edge:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source_id: str = ""
    target_id: str = ""
    edge_type: EdgeType = EdgeType.RELATION
    weight: float = 1.0
    bidirectional: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)

    def __post_init__(self) -> None:
        if not self.source_id or not self.target_id:
            raise ValueError("Edge requires source_id and target_id")
        if self.source_id == self.target_id:
            raise ValueError("Edge cannot connect a node to itself")
        self.weight = max(0.0, min(1.0, self.weight))

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "edge_type": self.edge_type.value,
            "weight": self.weight,
            "bidirectional": self.bidirectional,
            "metadata": self.metadata,
            "created_at": self.created_at,
        }
