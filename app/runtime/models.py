"""Models do Runtime pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
import time
import uuid

from app.runtime.constants import Complexity


@dataclass(slots=True)
class RuntimeRequest:
    message: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str | None = None
    session_id: str | None = None
    channel: str = "default"
    correlation_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)


@dataclass(slots=True)
class RuntimeResponse:
    text: str
    request_id: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str | None = None
    complexity: Complexity = Complexity.NORMAL
    modules_used: list[str] = field(default_factory=list)
    confidence: float = 0.5
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "request_id": self.request_id,
            "session_id": self.session_id,
            "text": self.text,
            "complexity": self.complexity.value,
            "modules_used": list(self.modules_used),
            "confidence": self.confidence,
            "metadata": self.metadata,
            "created_at": self.created_at,
        }
