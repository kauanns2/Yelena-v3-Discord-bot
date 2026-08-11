"""Tracing leve com correlation/trace/span IDs."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
import time
import uuid


@dataclass(slots=True)
class Span:
    name: str
    trace_id: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    parent_id: str | None = None
    correlation_id: str | None = None
    started_at: float = field(default_factory=time.time)
    ended_at: float | None = None
    attributes: dict[str, Any] = field(default_factory=dict)

    def end(self) -> None:
        self.ended_at = time.time()

    @property
    def duration_ms(self) -> float | None:
        if self.ended_at is None:
            return None
        return (self.ended_at - self.started_at) * 1000

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "trace_id": self.trace_id,
            "parent_id": self.parent_id,
            "name": self.name,
            "correlation_id": self.correlation_id,
            "started_at": self.started_at,
            "ended_at": self.ended_at,
            "duration_ms": self.duration_ms,
            "attributes": self.attributes,
        }


class Tracer:
    def __init__(self) -> None:
        self._spans: list[Span] = []

    def start_span(
        self,
        name: str,
        *,
        trace_id: str | None = None,
        parent_id: str | None = None,
        correlation_id: str | None = None,
        **attributes: Any,
    ) -> Span:
        span = Span(
            name=name,
            trace_id=trace_id or str(uuid.uuid4()),
            parent_id=parent_id,
            correlation_id=correlation_id,
            attributes=attributes,
        )
        self._spans.append(span)
        return span

    def recent(self, n: int = 50) -> list[Span]:
        return self._spans[-n:]
