"""Exceções do Memory System."""

from __future__ import annotations

from typing import Any


class MemoryError(Exception):
    def __init__(self, message: str, *, context: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.context = context or {}

    def __str__(self) -> str:
        if self.context:
            return f"{self.message} | context={self.context}"
        return self.message


class MemoryNotFoundError(MemoryError):
    pass


class MemoryValidationError(MemoryError):
    pass


class MemoryStoreError(MemoryError):
    pass


class MemoryAccessError(MemoryError):
    pass
