"""Afirmação com suporte a confiança e contestação."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
import time
import uuid

from app.knowledge.constants import KnowledgeStatus, DEFAULT_CONFIDENCE


@dataclass(slots=True)
class Assertion:
    claim: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    confidence: float = DEFAULT_CONFIDENCE
    status: KnowledgeStatus = KnowledgeStatus.ACTIVE
    supports: list[str] = field(default_factory=list)  # fact/evidence ids
    contradicts: list[str] = field(default_factory=list)
    source: str = ""
    version: int = 1
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.claim or not self.claim.strip():
            raise ValueError("Assertion claim is required")
        self.confidence = max(0.0, min(1.0, self.confidence))

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "claim": self.claim,
            "confidence": self.confidence,
            "status": self.status.value,
            "supports": list(self.supports),
            "contradicts": list(self.contradicts),
            "source": self.source,
            "version": self.version,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "metadata": self.metadata,
        }
