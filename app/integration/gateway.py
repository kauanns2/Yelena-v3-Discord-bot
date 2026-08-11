"""Gateway fino sobre YelenaRuntime.

Não contém lógica Discord. Não reescreve o Runtime.
"""

from __future__ import annotations

import logging
from typing import Any

from app.integration.contracts import ProcessMessageRequest, ProcessMessageResponse
from app.runtime import YelenaRuntime
from app.runtime.constants import RuntimeState
from app.runtime.errors import RuntimeNotStartedError

logger = logging.getLogger(__name__)


class YelenaGateway:
    """Ponto de integração para o intermediário existente."""

    def __init__(self, runtime: YelenaRuntime | None = None) -> None:
        self.runtime = runtime or YelenaRuntime()

    @property
    def state(self) -> str:
        return self.runtime.state.value

    def start(self) -> None:
        if self.runtime.state == RuntimeState.CREATED:
            self.runtime.bootstrap()
        if self.runtime.state != RuntimeState.READY:
            self.runtime.start()
        logger.info("YelenaGateway started", extra={"state": self.state})

    def stop(self) -> None:
        self.runtime.stop()
        logger.info("YelenaGateway stopped")

    def health(self) -> dict[str, Any]:
        data = self.runtime.health()
        data["gateway"] = "ok" if self.runtime.state in {RuntimeState.READY, RuntimeState.DEGRADED} else "not_ready"
        return data

    def process(self, request: ProcessMessageRequest | dict[str, Any] | str) -> ProcessMessageResponse:
        if self.runtime.state not in {RuntimeState.READY, RuntimeState.DEGRADED}:
            raise RuntimeNotStartedError(
                f"Runtime not ready: {self.runtime.state.value}",
                context={"state": self.runtime.state.value},
            )

        if isinstance(request, str):
            req = ProcessMessageRequest(message=request)
        elif isinstance(request, dict):
            req = ProcessMessageRequest.from_dict(request)
        else:
            req = request

        result = self.runtime.process(
            req.message,
            user_id=req.user_id,
            session_id=req.session_id,
            channel=req.channel,
            correlation_id=req.correlation_id,
        )

        return ProcessMessageResponse(
            text=result.text,
            request_id=result.request_id,
            session_id=result.session_id,
            complexity=result.complexity.value if hasattr(result.complexity, "value") else str(result.complexity),
            modules_used=list(result.modules_used),
            confidence=result.confidence,
            metadata=dict(result.metadata),
        )
