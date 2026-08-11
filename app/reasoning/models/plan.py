"""Plan e ActionProposal."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
import time
import uuid


@dataclass(slots=True)
class PlanStep:
    description: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    order: int = 0
    requires_authorization: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "description": self.description,
            "order": self.order,
            "requires_authorization": self.requires_authorization,
            "metadata": self.metadata,
        }


@dataclass(slots=True)
class Plan:
    goal: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    steps: list[PlanStep] = field(default_factory=list)
    confidence: float = 0.5
    created_at: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "goal": self.goal,
            "steps": [s.to_dict() for s in self.steps],
            "confidence": self.confidence,
            "created_at": self.created_at,
            "metadata": self.metadata,
        }


@dataclass(slots=True)
class ActionProposal:
    """Proposta de ação — NÃO é execução."""

    description: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    action_type: str = "generic"
    requires_authorization: bool = True
    risk: str = "low"
    parameters: dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.5
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "description": self.description,
            "action_type": self.action_type,
            "requires_authorization": self.requires_authorization,
            "risk": self.risk,
            "parameters": self.parameters,
            "confidence": self.confidence,
            "metadata": self.metadata,
        }
