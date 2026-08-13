"""Gateway fino sobre YelenaRuntime."""

from __future__ import annotations

import logging
import os
from typing import Any

from app.integration.contracts import ProcessMessageRequest, ProcessMessageResponse
from app.runtime import YelenaRuntime
from app.runtime.constants import RuntimeState
from app.runtime.errors import RuntimeNotStartedError

logger = logging.getLogger(__name__)


class YelenaGateway:
    def __init__(self, runtime: YelenaRuntime | None = None) -> None:
        self.runtime = runtime or YelenaRuntime()
        self._discord_started = False
        self._discord_error: str | None = None

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
        logger.info("YelenaGateway started state=%s", self.state)

    async def start_discord_if_configured(self) -> None:
        bridge = self.bridge
        if bridge is None:
            self._discord_error = "bridge_missing"
            return
        token = os.getenv("DISCORD_TOKEN", "").strip()
        if not token:
            self._discord_error = "DISCORD_TOKEN empty"
            logger.error(
                "Discord OFFLINE: variável DISCORD_TOKEN não está definida no Render"
            )
            return
        logger.info("Discord token present (len=%s) — starting adapter", len(token))
        try:
            adapter = bridge.register_discord(token=token)
            await adapter.start()
            self._discord_started = True
            self._discord_error = None
            logger.info("Discord adapter started — bot should go online")
        except Exception as exc:
            self._discord_error = str(exc)[:200]
            logger.exception("Discord adapter FAILED: %s", exc)

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
        if self._discord_error:
            data["discord_error"] = self._discord_error
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
