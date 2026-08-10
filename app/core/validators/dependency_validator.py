"""Validação de dependências."""

from __future__ import annotations

from app.core.dependency import DependencyResolver
from app.core.exceptions import ValidationError
from app.core.registry import ModuleRegistry


def validate_dependencies(registry: ModuleRegistry) -> None:
    resolver = DependencyResolver(registry)
    try:
        resolver.validate()
    except Exception as exc:
        raise ValidationError(str(exc)) from exc
