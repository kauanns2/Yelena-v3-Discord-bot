"""Exceções do Event Bus."""

from __future__ import annotations

from typing import Any


class EventBusError(Exception):
    def __init__(self, message: str, *, context: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.context = context or {}

    def __str__(self) -> str:
        if self.context:
            return f"{self.message} | context={self.context}"
        return self.message


class PublishError(EventBusError):
    pass


class SubscriptionError(EventBusError):
    pass


class DispatchError(EventBusError):
    pass


class EventValidationError(EventBusError):
    pass


class EventExpiredError(EventBusError):
    pass


class QueueFullError(EventBusError):
    pass
