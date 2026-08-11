"""ResponseSpecification — contrato para o Language module."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
import time
import uuid


@dataclass(slots=True)
class ResponseSpecification:
    """O que deve ser dito, não como gerar o texto final."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str = ""
    intent: str = ""
    goals: list[str] = field(default_factory=list)
    key_points: list[str] = field(default_factory=list)
    tone: str = "neutral"
    style_hints: dict[str, Any] = field(default_factory=dict)
    context_summary: list[str] = field(default_factory=list)
    decision_summary: str = ""
    should_ask_clarification: bool = False
    clarification_question: str | None = None
    should_confirm: bool = False
    constraints: list[str] = field(default_factory=list)
    max_length: str = "medium"  # short | medium | long
    language: str = "pt-BR"
    correlation_id: str | None = None
    created_at: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "session_id": self.session_id,
            "intent": self.intent,
            "goals": list(self.goals),
            "key_points": list(self.key_points),
            "tone": self.tone,
            "style_hints": self.style_hints,
            "context_summary": list(self.context_summary),
            "decision_summary": self.decision_summary,
            "should_ask_clarification": self.should_ask_clarification,
            "clarification_question": self.clarification_question,
            "should_confirm": self.should_confirm,
            "constraints": list(self.constraints),
            "max_length": self.max_length,
            "language": self.language,
            "correlation_id": self.correlation_id,
            "created_at": self.created_at,
            "metadata": self.metadata,
        }
