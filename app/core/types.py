"""Tipos e aliases do Core."""

from __future__ import annotations

from typing import Any, Callable, Awaitable, TypeAlias

ModuleId: TypeAlias = str
CorrelationId: TypeAlias = str
TraceId: TypeAlias = str

AsyncCallback: TypeAlias = Callable[..., Awaitable[Any]]
SyncCallback: TypeAlias = Callable[..., Any]
