"""Contratos estáveis para o intermediário Discord + IA.

O protocolo específico do intermediário NÃO está neste repositório.
Estes DTOs definem a borda mínima que qualquer intermediário pode usar.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ProcessMessageRequest:
    """Entrada esperada pelo Gateway / HTTP API."""

    message: str
    user_id: str | None = None
    session_id: str | None = None
    channel: str = "default"
    correlation_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ProcessMessageRequest:
        if not isinstance(data, dict):
            raise TypeError("request must be a dict")
        message = data.get("message")
        if not isinstance(message, str) or not message.strip():
            raise ValueError("message is required and must be a non-empty string")
        return cls(
            message=message,
            user_id=data.get("user_id"),
            session_id=data.get("session_id"),
            channel=str(data.get("channel") or "default"),
            correlation_id=data.get("correlation_id"),
            metadata=dict(data.get("metadata") or {}),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "message": self.message,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "channel": self.channel,
            "correlation_id": self.correlation_id,
            "metadata": self.metadata,
        }


@dataclass(slots=True)
class ProcessMessageResponse:
    """Saída estável para o intermediário devolver ao Discord."""

    text: str
    request_id: str
    session_id: str | None = None
    complexity: str = "normal"
    modules_used: list[str] = field(default_factory=list)
    confidence: float = 0.5
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "text": self.text,
            "request_id": self.request_id,
            "session_id": self.session_id,
            "complexity": self.complexity,
            "modules_used": list(self.modules_used),
            "confidence": self.confidence,
            "metadata": self.metadata,
        }
