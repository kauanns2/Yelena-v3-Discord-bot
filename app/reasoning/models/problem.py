"""Problem, Goal, Constraint."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
import time
import uuid


@dataclass(slots=True)
class Goal:
    description: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    priority: float = 0.5
    success_criteria: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "description": self.description,
            "priority": self.priority,
            "success_criteria": list(self.success_criteria),
            "metadata": self.metadata,
        }


@dataclass(slots=True)
class Constraint:
    description: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    hard: bool = True
    source: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "description": self.description,
            "hard": self.hard,
            "source": self.source,
            "metadata": self.metadata,
        }


@dataclass(slots=True)
class Problem:
    description: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    goals: list[Goal] = field(default_factory=list)
    constraints: list[Constraint] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)
    unknowns: list[str] = field(default_factory=list)
    context_summary: str = ""
    session_id: str | None = None
    user_id: str | None = None
    correlation_id: str | None = None
    created_at: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.description or not self.description.strip():
            raise ValueError("Problem description is required")

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "description": self.description,
            "goals": [g.to_dict() for g in self.goals],
            "constraints": [c.to_dict() for c in self.constraints],
            "assumptions": list(self.assumptions),
            "unknowns": list(self.unknowns),
            "context_summary": self.context_summary,
            "session_id": self.session_id,
            "user_id": self.user_id,
            "correlation_id": self.correlation_id,
            "created_at": self.created_at,
            "metadata": self.metadata,
        }
