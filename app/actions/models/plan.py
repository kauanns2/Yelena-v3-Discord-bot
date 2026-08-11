"""ActionPlan e ActionStep."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
import time
import uuid

from app.actions.models.request import ActionRequest


@dataclass(slots=True)
class ActionStep:
    request: ActionRequest
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    order: int = 0
    depends_on: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "order": self.order,
            "depends_on": list(self.depends_on),
            "request": self.request.to_dict(),
        }


@dataclass(slots=True)
class ActionPlan:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    steps: list[ActionStep] = field(default_factory=list)
    goal: str = ""
    created_at: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "goal": self.goal,
            "steps": [s.to_dict() for s in self.steps],
            "created_at": self.created_at,
            "metadata": self.metadata,
        }
