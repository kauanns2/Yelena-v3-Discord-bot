"""Nó da Teia Neural."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
import time
import uuid

from app.neural.constants import NodeType, NodeStatus


@dataclass(slots=True)
class Node:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    node_type: NodeType = NodeType.CUSTOM
    status: NodeStatus = NodeStatus.ACTIVE
    module_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)

    def __post_init__(self) -> None:
        if not self.name:
            self.name = self.id

    @property
    def is_active(self) -> bool:
        return self.status == NodeStatus.ACTIVE

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "node_type": self.node_type.value,
            "status": self.status.value,
            "module_id": self.module_id,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
