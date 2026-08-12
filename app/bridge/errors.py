"""Exceções do Bridge (Módulo 17)."""

from __future__ import annotations

from typing import Any


class BridgeError(Exception):
    def __init__(self, message: str, *, context: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.context = context or {}


class PlatformError(BridgeError):
    pass


class ContinuityError(BridgeError):
    pass


class EvolutionError(BridgeError):
    pass
