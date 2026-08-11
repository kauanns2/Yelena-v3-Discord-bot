"""Verificação básica de permissões de ação.

A autoridade final de segurança fica no Módulo 14.
Aqui: checagens locais de risk + confirmation.
"""

from __future__ import annotations

from app.actions.constants import RiskLevel
from app.actions.errors import PermissionDeniedError, ConfirmationRequiredError
from app.actions.models.request import ActionRequest
from app.actions.models.tool import Tool


class PermissionChecker:
    """Least privilege local. Security module é a autoridade final."""

    def check(self, tool: Tool, request: ActionRequest) -> None:
        if not tool.enabled:
            raise PermissionDeniedError(
                f"Tool disabled: {tool.id}",
                context={"tool_id": tool.id},
            )

        risk = request.risk_hint or tool.risk

        needs_confirmation = (
            request.requires_confirmation
            or tool.capabilities.requires_confirmation
            or risk in {RiskLevel.HIGH, RiskLevel.CRITICAL}
        )

        if needs_confirmation and not request.confirmed and not request.dry_run:
            raise ConfirmationRequiredError(
                f"Confirmation required for tool: {tool.id}",
                context={"tool_id": tool.id, "risk": risk.value},
            )
