"""Executor de ações."""

from __future__ import annotations

import logging
import time
from typing import Any

from app.actions.constants import ActionStatus, DEFAULT_TIMEOUT
from app.actions.errors import ExecutionError, TimeoutError as ActionTimeoutError
from app.actions.models.request import ActionRequest
from app.actions.models.result import ActionResult
from app.actions.models.tool import Tool

logger = logging.getLogger(__name__)


class ActionExecutor:
    """Executa o handler da tool com timeout e dry-run."""

    def execute(self, tool: Tool, request: ActionRequest) -> ActionResult:
        start = time.perf_counter()
        result = ActionResult(
            request_id=request.id,
            tool_id=tool.id,
            risk=request.risk_hint or tool.risk,
            dry_run=request.dry_run,
            correlation_id=request.correlation_id,
            status=ActionStatus.RUNNING,
        )

        if request.dry_run:
            result.status = ActionStatus.SUCCEEDED
            result.success = True
            result.output = {
                "dry_run": True,
                "tool_id": tool.id,
                "arguments": request.arguments,
                "message": "Dry-run: no side effects applied",
            }
            result.duration_ms = (time.perf_counter() - start) * 1000
            return result

        if tool.handler is None:
            result.status = ActionStatus.FAILED
            result.error = f"Tool has no handler: {tool.id}"
            result.duration_ms = (time.perf_counter() - start) * 1000
            return result

        timeout = request.timeout or DEFAULT_TIMEOUT
        try:
            # execução síncrona simples; async/timeout avançado em evolução
            output = tool.handler(**request.arguments)
            result.output = output
            result.success = True
            result.status = ActionStatus.SUCCEEDED
        except Exception as exc:
            result.success = False
            result.status = ActionStatus.FAILED
            result.error = str(exc)
            logger.exception("action execution failed", extra={"tool_id": tool.id})

        result.duration_ms = (time.perf_counter() - start) * 1000
        if result.duration_ms > timeout * 1000 and result.success:
            # marca aviso; timeout real exigiria thread/async cancel
            result.metadata["timeout_warning"] = True

        return result
