"""Contratos e protocolos fundamentais do Core.

O Core conhece contratos, não detalhes de implementação.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from app.core.constants import HealthStatus, LifecycleState


@runtime_checkable
class ModuleProtocol(Protocol):
    """Contrato mínimo de um módulo da Yelena."""

    @property
    def id(self) -> str: ...

    @property
    def name(self) -> str: ...

    @property
    def version(self) -> str: ...

    @property
    def state(self) -> LifecycleState: ...

    async def initialize(self) -> None: ...

    async def start(self) -> None: ...

    async def stop(self) -> None: ...

    async def health(self) -> "HealthCheckResult": ...


@runtime_checkable
class HealthCheck(Protocol):
    """Contrato de health check."""

    async def check(self) -> "HealthCheckResult": ...


@runtime_checkable
class ShutdownHandler(Protocol):
    """Contrato de handler de shutdown."""

    async def on_shutdown(self) -> None: ...


@runtime_checkable
class Configurable(Protocol):
    """Contrato para componentes que recebem configuração."""

    def configure(self, config: Any) -> None: ...


class HealthCheckResult:
    """Resultado de um health check."""

    __slots__ = ("status", "message", "details", "latency_ms", "timestamp")

    def __init__(
        self,
        status: HealthStatus,
        message: str = "",
        details: dict[str, Any] | None = None,
        latency_ms: float = 0.0,
        timestamp: float | None = None,
    ) -> None:
        import time

        self.status = status
        self.message = message
        self.details = details or {}
        self.latency_ms = latency_ms
        self.timestamp = timestamp if timestamp is not None else time.time()

    @property
    def is_healthy(self) -> bool:
        return self.status == HealthStatus.HEALTHY

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status.value,
            "message": self.message,
            "details": self.details,
            "latency_ms": self.latency_ms,
            "timestamp": self.timestamp,
        }
