"""ConversationSession e Participant."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
import time
import uuid

from app.conversation.constants import SessionStatus, DEFAULT_SESSION_TTL


@dataclass(slots=True)
class Participant:
    id: str
    role: str = "user"
    name: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "role": self.role,
            "name": self.name,
            "metadata": self.metadata,
        }


@dataclass(slots=True)
class ConversationSession:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str | None = None
    channel: str = "default"
    status: SessionStatus = SessionStatus.ACTIVE
    participants: list[Participant] = field(default_factory=list)
    turn_ids: list[str] = field(default_factory=list)
    current_topic: str | None = None
    topic_stack: list[str] = field(default_factory=list)
    pending_questions: list[str] = field(default_factory=list)
    goals: list[str] = field(default_factory=list)
    last_intent: str | None = None
    last_activity: float = field(default_factory=time.time)
    created_at: float = field(default_factory=time.time)
    expires_at: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.expires_at is None:
            self.expires_at = self.created_at + DEFAULT_SESSION_TTL

    @property
    def is_expired(self) -> bool:
        return self.expires_at is not None and time.time() > self.expires_at

    def touch(self) -> None:
        self.last_activity = time.time()
        if self.expires_at is not None:
            self.expires_at = time.time() + DEFAULT_SESSION_TTL

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "channel": self.channel,
            "status": self.status.value,
            "participants": [p.to_dict() for p in self.participants],
            "turn_count": len(self.turn_ids),
            "current_topic": self.current_topic,
            "topic_stack": list(self.topic_stack),
            "pending_questions": list(self.pending_questions),
            "goals": list(self.goals),
            "last_intent": self.last_intent,
            "last_activity": self.last_activity,
            "created_at": self.created_at,
            "expires_at": self.expires_at,
            "metadata": self.metadata,
        }
