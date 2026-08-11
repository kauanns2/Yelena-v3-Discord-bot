"""Exceções do Observability System."""

from __future__ import annotations

from typing import Any


class ObservabilityError(Exception):
    def __init__(self, message: str, *, context: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.context = context or {}
