"""Decision, Alternative, Hypothesis."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
import time
import uuid

from app.reasoning.constants import DecisionStatus, StrategyType, RiskLevel


@dataclass(slots=True)
class Hypothesis:
    statement: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    confidence: float = 0.5
    evidence: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "statement": self.statement,
            "confidence": self.confidence,
            "evidence": list(self.evidence),
            "metadata": self.metadata,
        }


@dataclass(slots=True)
class Alternative:
    description: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    score: float = 0.0
    pros: list[str] = field(default_factory=list)
    cons: list[str] = field(default_factory=list)
    risk: RiskLevel = RiskLevel.LOW
    confidence: float = 0.5
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "description": self.description,
            "score": self.score,
            "pros": list(self.pros),
            "cons": list(self.cons),
            "risk": self.risk.value,
            "confidence": self.confidence,
            "metadata": self.metadata,
        }


@dataclass(slots=True)
class Decision:
    problem_id: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: DecisionStatus = DecisionStatus.PENDING
    strategy: StrategyType = StrategyType.DIRECT
    selected: Alternative | None = None
    alternatives: list[Alternative] = field(default_factory=list)
    hypotheses: list[Hypothesis] = field(default_factory=list)
    confidence: float = 0.0
    uncertainty: float = 0.0
    ambiguity: bool = False
    needs_info: list[str] = field(default_factory=list)
    risk: RiskLevel = RiskLevel.NONE
    explanation_id: str | None = None
    plan_id: str | None = None
    correlation_id: str | None = None
    created_at: float = field(default_factory=time.time)
    completed_at: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "problem_id": self.problem_id,
            "status": self.status.value,
            "strategy": self.strategy.value,
            "selected": self.selected.to_dict() if self.selected else None,
            "alternatives": [a.to_dict() for a in self.alternatives],
            "hypotheses": [h.to_dict() for h in self.hypotheses],
            "confidence": self.confidence,
            "uncertainty": self.uncertainty,
            "ambiguity": self.ambiguity,
            "needs_info": list(self.needs_info),
            "risk": self.risk.value,
            "explanation_id": self.explanation_id,
            "plan_id": self.plan_id,
            "correlation_id": self.correlation_id,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
            "metadata": self.metadata,
        }
