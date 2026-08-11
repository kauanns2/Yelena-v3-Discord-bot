"""Explicação resumida da decisão."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
import time
import uuid


@dataclass(slots=True)
class Explanation:
    summary: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    reasons: list[str] = field(default_factory=list)
    rejected: list[str] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)
    confidence: float = 0.5
    created_at: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "summary": self.summary,
            "reasons": list(self.reasons),
            "rejected": list(self.rejected),
            "assumptions": list(self.assumptions),
            "confidence": self.confidence,
            "created_at": self.created_at,
            "metadata": self.metadata,
        }
