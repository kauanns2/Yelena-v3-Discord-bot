"""Action Manager."""

from __future__ import annotations

import logging
from typing import Any, Callable

from app.actions.constants import RiskLevel, ActionStatus, ToolCategory
from app.actions.errors import (
    ConfirmationRequiredError,
    PermissionDeniedError,
    ValidationError,
)
from app.actions.executor import ActionExecutor
from app.actions.models.request import ActionRequest
from app.actions.models.result import ActionResult
from app.actions.models.tool import Tool, ToolCapabilities
from app.actions.models.plan import ActionPlan, ActionStep
from app.actions.permissions import PermissionChecker
from app.actions.registry import ToolRegistry
from app.actions.validation import validate_request

logger = logging.getLogger(__name__)


class ActionManager:
    """Coordena registro de tools e execução controlada.

    Fluxo: validate → permission → (confirm) → execute → result
    """

    def __init__(self) -> None:
        self.registry = ToolRegistry()
        self._executor = ActionExecutor()
        self._permissions = PermissionChecker()
        self._started = False
        self._metrics = {
            "actions_requested": 0,
            "actions_succeeded": 0,
            "actions_failed": 0,
            "actions_denied": 0,
            "dry_runs": 0,
        }
        self._register_builtin_tools()

    def _register_builtin_tools(self) -> None:
        def echo_handler(message: str = "") -> dict[str, str]:
            return {"echo": message}

        self.registry.register(
            Tool(
                id="echo",
                name="Echo",
                description="Retorna a mensagem (utilitário seguro)",
                category=ToolCategory.UTILITY,
                risk=RiskLevel.NONE,
                capabilities=ToolCapabilities(
                    dry_run=True,
                    idempotent=True,
                    requires_confirmation=False,
                    side_effects=False,
                ),
                parameters_schema={
                    "required": ["message"],
                    "properties": {"message": {"type": "string"}},
                    "additionalProperties": False,
                },
                handler=echo_handler,
            )
        )

    @property
    def is_started(self) -> bool:
        return self._started

    def start(self) -> None:
        self._started = True
        logger.info("action system started", extra={"tools": self.registry.list_ids()})

    def stop(self) -> None:
        self._started = False

    def register_tool(self, tool: Tool) -> None:
        self.registry.register(tool)

    def execute(self, request: ActionRequest) -> ActionResult:
        self._metrics["actions_requested"] += 1
        if request.dry_run:
            self._metrics["dry_runs"] += 1

        try:
            tool = self.registry.require(request.tool_id)
            validate_request(tool, request)
            self._permissions.check(tool, request)

            result = self._executor.execute(tool, request)
            if result.success:
                self._metrics["actions_succeeded"] += 1
            else:
                self._metrics["actions_failed"] += 1
            return result

        except ConfirmationRequiredError as exc:
            self._metrics["actions_denied"] += 1
            return ActionResult(
                request_id=request.id,
                tool_id=request.tool_id,
                status=ActionStatus.AWAITING_CONFIRMATION,
                success=False,
                error=str(exc),
                risk=request.risk_hint or RiskLevel.HIGH,
                correlation_id=request.correlation_id,
            )
        except (PermissionDeniedError, ValidationError) as exc:
            self._metrics["actions_denied"] += 1
            return ActionResult(
                request_id=request.id,
                tool_id=request.tool_id,
                status=ActionStatus.DENIED,
                success=False,
                error=str(exc),
                correlation_id=request.correlation_id,
            )
        except Exception as exc:
            self._metrics["actions_failed"] += 1
            logger.exception("action failed")
            return ActionResult(
                request_id=request.id,
                tool_id=request.tool_id,
                status=ActionStatus.FAILED,
                success=False,
                error=str(exc),
                correlation_id=request.correlation_id,
            )

    def execute_plan(self, plan: ActionPlan) -> list[ActionResult]:
        results: list[ActionResult] = []
        ordered = sorted(plan.steps, key=lambda s: s.order)
        for step in ordered:
            results.append(self.execute(step.request))
        return results

    def health(self) -> dict[str, Any]:
        return {
            "status": "healthy" if self._started else "stopped",
            "tools": self.registry.list_ids(),
            "metrics": dict(self._metrics),
        }
