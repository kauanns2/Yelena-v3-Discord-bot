"""Subscription model."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable
import time
import uuid


@dataclass(slots=True)
class Subscription:
    event_name: str
    handler: Callable[..., Any]
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source_filter: str | None = None
    priority_min: int | None = None
    active: bool = True
    created_at: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)

    def matches(self, event: Any) -> bool:
        if not self.active:
            return False
        if self.event_name != "*" and self.event_name != event.name:
            # suporte a prefixo: "module.*"
            if self.event_name.endswith(".*"):
                prefix = self.event_name[:-1]  # keep trailing dot pattern
                if not event.name.startswith(self.event_name[:-1]):
                    return False
            else:
                return False
        if self.source_filter and event.source != self.source_filter:
            return False
        if self.priority_min is not None and event.priority.value < self.priority_min:
            return False
        return True
