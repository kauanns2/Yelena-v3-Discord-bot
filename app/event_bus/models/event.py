"""Modelo formal de evento."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
import time
import uuid

from app.event_bus.constants import EventPriority, EventStatus, DEFAULT_TTL


@dataclass(slots=True)
class Event:
    name: str
    payload: dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source: str = ""
    priority: EventPriority = EventPriority.NORMAL
    status: EventStatus = EventStatus.PENDING
    correlation_id: str | None = None
    causation_id: str | None = None
    trace_id: str | None = None
    ttl: float = DEFAULT_TTL
    created_at: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.name or not self.name.strip():
            raise ValueError("Event name is required")
        self.name = self.name.strip()

    @property
    def is_expired(self) -> bool:
        return (time.time() - self.created_at) > self.ttl

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "payload": self.payload,
            "source": self.source,
            "priority": self.priority.value,
            "status": self.status.value,
            "correlation_id": self.correlation_id,
            "causation_id": self.causation_id,
            "trace_id": self.trace_id,
            "ttl": self.ttl,
            "created_at": self.created_at,
            "metadata": self.metadata,
        }
