"""Contrato de plataforma — Discord, Telegram, etc."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable
import time
import uuid


@dataclass(slots=True)
class InboundMessage:
    text: str
    user_id: str
    channel_id: str
    platform: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str | None = None
    correlation_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)


@dataclass(slots=True)
class OutboundMessage:
    text: str
    channel_id: str
    user_id: str | None = None
    reply_to: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    # path local de áudio (mp3) para a plataforma enviar
    audio_path: str | None = None
    prefer_audio: bool = False


MessageHandler = Callable[[InboundMessage], Awaitable[OutboundMessage] | OutboundMessage]


class PlatformAdapter(ABC):
    """Qualquer bot futuro implementa isto."""

    @property
    @abstractmethod
    def platform_id(self) -> str: ...

    @abstractmethod
    async def start(self) -> None: ...

    @abstractmethod
    async def stop(self) -> None: ...

    @abstractmethod
    def set_handler(self, handler: MessageHandler) -> None: ...

    @abstractmethod
    async def send(self, message: OutboundMessage) -> None: ...

    def health(self) -> dict[str, Any]:
        return {"platform": self.platform_id, "status": "unknown"}
