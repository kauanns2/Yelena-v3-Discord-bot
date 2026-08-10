"""Exceções do Configuration System."""

from __future__ import annotations

from typing import Any


class ConfigurationError(Exception):
    def __init__(self, message: str, *, context: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.context = context or {}

    def __str__(self) -> str:
        if self.context:
            return f"{self.message} | context={self.context}"
        return self.message


class ConfigValidationError(ConfigurationError):
    """Configuração inválida."""


class ConfigMissingError(ConfigurationError):
    """Configuração obrigatória ausente."""


class SecretError(ConfigurationError):
    """Erro relacionado a secrets."""


class ConfigSourceError(ConfigurationError):
    """Erro em uma fonte de configuração."""


class OverrideForbiddenError(ConfigurationError):
    """Override proibido no ambiente atual."""
