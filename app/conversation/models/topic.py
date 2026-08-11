"""Topic model."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
import time
import uuid


@dataclass(slots=True)
class Topic:
    name: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    active: bool = True
    depth: int = 0
    parent_id: str | None = None
    created_at: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "active": self.active,
            "depth": self.depth,
            "parent_id": self.parent_id,
            "created_at": self.created_at,
            "metadata": self.metadata,
        }
