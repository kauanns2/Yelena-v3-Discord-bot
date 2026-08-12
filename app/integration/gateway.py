"""Gateway fino sobre YelenaRuntime.

Não contém lógica Discord. Discord fica no Bridge (Módulo 17).
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
    """Ponto de integração para HTTP e Bridge."""

    def __init__(self, runtime: YelenaRuntime | None = None) -> None:
        self.runtime = runtime or YelenaRuntime()
        self._discord_started = False

    @property
    def state(self) -> str:
        return self.runtime.state.value

    @property
    def bridge(self) -> Any:
        return getattr(self.runtime, "bridge", None)

    def start(self) -> None:
        if self.runtime.state == RuntimeState.CREATED:
            self.runtime.bootstrap()
        if self.runtime.state != RuntimeState.READY:
            self.runtime.start()
        logger.info("YelenaGateway started", extra={"state": self.state})

    async def start_discord_if_configured(self) -> None:
        """Sobe adapter Discord se DISCORD_TOKEN estiver definido."""
        bridge = self.bridge
        if bridge is None:
            return
        if not bridge.discord_token_configured():
            logger.info("DISCORD_TOKEN not set — Discord adapter skipped")
            return
        try:
            adapter = bridge.register_discord()
            await adapter.start()
            self._discord_started = True
            logger.info("Discord adapter started via Bridge")
        except Exception:
            logger.exception("failed to start Discord adapter")

    async def stop_discord(self) -> None:
        bridge = self.bridge
        if bridge is None:
            return
        adapter = bridge.platforms.get("discord")
        if adapter is not None:
            try:
                await adapter.stop()
            except Exception:
                logger.exception("error stopping Discord adapter")
        self._discord_started = False

    def stop(self) -> None:
        self.runtime.stop()
        logger.info("YelenaGateway stopped")

    def health(self) -> dict[str, Any]:
        data = self.runtime.health()
        data["gateway"] = (
            "ok"
            if self.runtime.state in {RuntimeState.READY, RuntimeState.DEGRADED}
            else "not_ready"
        )
        data["discord_adapter"] = "online" if self._discord_started else "offline"
        if self.bridge is not None:
            data["bridge"] = self.bridge.health()
        return data

    def process(
        self, request: ProcessMessageRequest | dict[str, Any] | str
    ) -> ProcessMessageResponse:
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
            complexity=result.complexity.value
            if hasattr(result.complexity, "value")
            else str(result.complexity),
            modules_used=list(result.modules_used),
            confidence=result.confidence,
            metadata=dict(result.metadata),
        )
