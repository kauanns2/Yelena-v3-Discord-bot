"""Validação de argumentos de ação."""

from __future__ import annotations

from typing import Any

from app.actions.errors import ValidationError
from app.actions.models.request import ActionRequest
from app.actions.models.tool import Tool


def validate_request(tool: Tool, request: ActionRequest) -> None:
    if not request.tool_id:
        raise ValidationError("tool_id is required")

    schema = tool.parameters_schema or {}
    required = schema.get("required", [])
    properties = schema.get("properties", {})

    for key in required:
        if key not in request.arguments:
            raise ValidationError(
                f"Missing required argument: {key}",
                context={"tool_id": tool.id, "argument": key},
            )

    # rejeitar argumentos desconhecidos se schema strict
    if properties and schema.get("additionalProperties") is False:
        for key in request.arguments:
            if key not in properties:
                raise ValidationError(
                    f"Unknown argument: {key}",
                    context={"tool_id": tool.id, "argument": key},
                )

    # bloqueios básicos de segurança em strings de path/comando
    for key, value in request.arguments.items():
        if isinstance(value, str):
            if "../" in value or "..\\" in value:
                raise ValidationError(
                    f"Path traversal blocked in argument: {key}",
                    context={"tool_id": tool.id, "argument": key},
                )
