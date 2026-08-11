"""Fato estruturado."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
import time
import uuid

from app.knowledge.constants import KnowledgeStatus, DEFAULT_CONFIDENCE


@dataclass(slots=True)
class Fact:
    statement: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    subject: str = ""
    predicate: str = ""
    object: str = ""
    confidence: float = DEFAULT_CONFIDENCE
    status: KnowledgeStatus = KnowledgeStatus.ACTIVE
    evidence_ids: list[str] = field(default_factory=list)  # memory ids
    source: str = ""
    valid_from: float | None = None
    valid_until: float | None = None
    version: int = 1
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.statement or not self.statement.strip():
            raise ValueError("Fact statement is required")
        self.confidence = max(0.0, min(1.0, self.confidence))

    @property
    def is_valid(self) -> bool:
        now = time.time()
        if self.status in {KnowledgeStatus.INVALIDATED, KnowledgeStatus.DEPRECATED}:
            return False
        if self.valid_from is not None and now < self.valid_from:
            return False
        if self.valid_until is not None and now > self.valid_until:
            return False
        return True

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "statement": self.statement,
            "subject": self.subject,
            "predicate": self.predicate,
            "object": self.object,
            "confidence": self.confidence,
            "status": self.status.value,
            "evidence_ids": list(self.evidence_ids),
            "source": self.source,
            "valid_from": self.valid_from,
            "valid_until": self.valid_until,
            "version": self.version,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "metadata": self.metadata,
        }
