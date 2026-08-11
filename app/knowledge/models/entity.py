"""Entidade de conhecimento."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
import time
import uuid


@dataclass(slots=True)
class Entity:
    name: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    entity_type: str = "generic"
    aliases: list[str] = field(default_factory=list)
    attributes: dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.7
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.name or not self.name.strip():
            raise ValueError("Entity name is required")

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "entity_type": self.entity_type,
            "aliases": list(self.aliases),
            "attributes": self.attributes,
            "confidence": self.confidence,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "metadata": self.metadata,
        }
