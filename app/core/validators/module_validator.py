"""Validação de módulos."""

from __future__ import annotations

from app.core.exceptions import ValidationError
from app.core.models.module import ModuleInfo


def validate_module(module: ModuleInfo) -> None:
    if not module.id or not module.id.strip():
        raise ValidationError("Module id is required")
    if not module.name or not module.name.strip():
        raise ValidationError(
            "Module name is required",
            context={"module_id": module.id},
        )
    if " " in module.id or module.id != module.id.lower():
        raise ValidationError(
            "Module id must be lowercase without spaces",
            context={"module_id": module.id},
        )
