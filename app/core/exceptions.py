"""Hierarquia de exceções do Core."""

from __future__ import annotations

from typing import Any


class CoreError(Exception):
    """Erro base do Core."""

    def __init__(self, message: str, *, context: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.context = context or {}

    def __str__(self) -> str:
        if self.context:
            return f"{self.message} | context={self.context}"
        return self.message


class BootstrapError(CoreError):
    """Falha durante o bootstrap."""


class LifecycleError(CoreError):
    """Erro de ciclo de vida ou transição inválida."""


class ModuleError(CoreError):
    """Erro relacionado a um módulo."""

    def __init__(
        self,
        message: str,
        *,
        module_id: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> None:
        ctx = dict(context or {})
        if module_id:
            ctx["module_id"] = module_id
        super().__init__(message, context=ctx)
        self.module_id = module_id


class DependencyError(CoreError):
    """Erro de dependência (ausente, ciclo, incompatível)."""


class RegistryError(CoreError):
    """Erro no registro de módulos."""


class LoaderError(CoreError):
    """Erro ao carregar módulo."""


class ValidationError(CoreError):
    """Erro de validação de contratos ou estado."""


class ShutdownError(CoreError):
    """Erro durante o encerramento."""


class ConfigurationError(CoreError):
    """Erro de configuração do Core."""


class HealthError(CoreError):
    """Erro no sistema de health."""
