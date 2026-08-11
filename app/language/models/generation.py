"""GenerationRequest e GenerationResult."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
import time
import uuid

from app.language.constants import GenerationStatus, OutputFormat, LengthHint


@dataclass(slots=True)
class GenerationRequest:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    instructions: str = ""
    style: dict[str, Any] = field(default_factory=dict)
    context_blocks: list[str] = field(default_factory=list)
    key_points: list[str] = field(default_factory=list)
    language: str = "pt-BR"
    output_format: OutputFormat = OutputFormat.TEXT
    length: LengthHint = LengthHint.MEDIUM
    max_tokens: int = 512
    temperature: float = 0.7
    correlation_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "instructions": self.instructions,
            "style": self.style,
            "context_blocks": list(self.context_blocks),
            "key_points": list(self.key_points),
            "language": self.language,
            "output_format": self.output_format.value,
            "length": self.length.value,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "correlation_id": self.correlation_id,
            "metadata": self.metadata,
        }


@dataclass(slots=True)
class GenerationResult:
    text: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: GenerationStatus = GenerationStatus.SUCCESS
    provider_id: str = ""
    request_id: str | None = None
    confidence: float = 0.7
    finish_reason: str = "completed"
    usage: dict[str, int] = field(default_factory=dict)
    correlation_id: str | None = None
    created_at: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "text": self.text,
            "status": self.status.value,
            "provider_id": self.provider_id,
            "request_id": self.request_id,
            "confidence": self.confidence,
            "finish_reason": self.finish_reason,
            "usage": self.usage,
            "correlation_id": self.correlation_id,
            "created_at": self.created_at,
            "metadata": self.metadata,
        }
