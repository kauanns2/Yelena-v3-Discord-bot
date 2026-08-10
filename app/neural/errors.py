"""Exceções da Neural Web."""

from __future__ import annotations

from typing import Any


class NeuralError(Exception):
    def __init__(self, message: str, *, context: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.context = context or {}

    def __str__(self) -> str:
        if self.context:
            return f"{self.message} | context={self.context}"
        return self.message


class NodeError(NeuralError):
    pass


class EdgeError(NeuralError):
    pass


class SignalError(NeuralError):
    pass


class PropagationError(NeuralError):
    pass


class LoopDetectedError(PropagationError):
    pass


class TTLExpiredError(PropagationError):
    pass


class TopologyError(NeuralError):
    pass
