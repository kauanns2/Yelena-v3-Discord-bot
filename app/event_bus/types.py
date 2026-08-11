"""Tipos do Event Bus."""

from __future__ import annotations

from typing import Any, Callable, Awaitable, TypeAlias

EventName: TypeAlias = str
SubscriptionId: TypeAlias = str
CorrelationId: TypeAlias = str

EventHandler: TypeAlias = Callable[..., Any]
AsyncEventHandler: TypeAlias = Callable[..., Awaitable[Any]]
