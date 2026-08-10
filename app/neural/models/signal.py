"""Sinal que percorre a Teia."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
import time
import uuid

from app.neural.constants import SignalType, SignalPriority, DEFAULT_TTL, DEFAULT_MAX_HOPS


@dataclass(slots=True)
class Signal:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    signal_type: SignalType = SignalType.EVENT
    source_id: str = ""
    target_id: str | None = None  # None = broadcast limitado pela topologia
    payload: dict[str, Any] = field(default_factory=dict)
    priority: SignalPriority = SignalPriority.NORMAL
    ttl: float = DEFAULT_TTL
    max_hops: int = DEFAULT_MAX_HOPS
    hops: int = 0
    path: list[str] = field(default_factory=list)
    correlation_id: str | None = None
    created_at: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def is_expired(self) -> bool:
        return (time.time() - self.created_at) > self.ttl

    @property
    def can_propagate(self) -> bool:
        return not self.is_expired and self.hops < self.max_hops

    def hop(self, node_id: str) -> None:
        self.hops += 1
        self.path.append(node_id)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "signal_type": self.signal_type.value,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "payload": self.payload,
            "priority": self.priority.value,
            "ttl": self.ttl,
            "max_hops": self.max_hops,
            "hops": self.hops,
            "path": list(self.path),
            "correlation_id": self.correlation_id,
            "created_at": self.created_at,
            "metadata": self.metadata,
        }
