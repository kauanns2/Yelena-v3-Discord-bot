"""Exceções do Cognitive Context System."""

from __future__ import annotations

from typing import Any


class ContextError(Exception):
    def __init__(self, message: str, *, context: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.context = context or {}

    def __str__(self) -> str:
        if self.context:
            return f"{self.message} | context={self.context}"
        return self.message


class ContextBuildError(ContextError):
    pass


class ContextBudgetError(ContextError):
    pass
