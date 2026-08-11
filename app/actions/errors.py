"""Exceções do Action System."""

from __future__ import annotations

from typing import Any


class ActionError(Exception):
    def __init__(self, message: str, *, context: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.context = context or {}

    def __str__(self) -> str:
        if self.context:
            return f"{self.message} | context={self.context}"
        return self.message


class ToolNotFoundError(ActionError):
    pass


class PermissionDeniedError(ActionError):
    pass


class ValidationError(ActionError):
    pass


class ConfirmationRequiredError(ActionError):
    pass


class ExecutionError(ActionError):
    pass


class TimeoutError(ActionError):
    pass
