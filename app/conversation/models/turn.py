"""Turn e Intent."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
import time
import uuid

from app.conversation.constants import IntentType, TurnRole


@dataclass(slots=True)
class Intent:
    intent_type: IntentType = IntentType.UNKNOWN
    confidence: float = 0.5
    entities: list[str] = field(default_factory=list)
    raw: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "intent_type": self.intent_type.value,
            "confidence": self.confidence,
            "entities": list(self.entities),
            "raw": self.raw,
            "metadata": self.metadata,
        }


@dataclass(slots=True)
class Turn:
    content: str
    role: TurnRole = TurnRole.USER
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str = ""
    intent: Intent | None = None
    intents: list[Intent] = field(default_factory=list)  # multi-intent
    topic: str | None = None
    references: list[str] = field(default_factory=list)
    correlation_id: str | None = None
    created_at: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "session_id": self.session_id,
            "role": self.role.value,
            "content": self.content,
            "intent": self.intent.to_dict() if self.intent else None,
            "intents": [i.to_dict() for i in self.intents],
            "topic": self.topic,
            "references": list(self.references),
            "correlation_id": self.correlation_id,
            "created_at": self.created_at,
            "metadata": self.metadata,
        }
