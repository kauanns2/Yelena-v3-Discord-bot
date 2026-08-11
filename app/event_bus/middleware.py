"""Middleware pipeline do Event Bus."""

from __future__ import annotations

import logging
from typing import Any, Callable

from app.event_bus.models.event import Event

logger = logging.getLogger(__name__)

Middleware = Callable[[Event], Event | None]
# Retornar None = drop event


class MiddlewarePipeline:
    def __init__(self) -> None:
        self._middlewares: list[Middleware] = []

    def use(self, middleware: Middleware) -> None:
        self._middlewares.append(middleware)

    def run(self, event: Event) -> Event | None:
        current: Event | None = event
        for mw in self._middlewares:
            if current is None:
                return None
            try:
                current = mw(current)
            except Exception:
                logger.exception("middleware failed", extra={"event": event.name})
                raise
        return current


def ttl_middleware(event: Event) -> Event | None:
    if event.is_expired:
        logger.debug("event expired dropped", extra={"event_id": event.id})
        return None
    return event


def logging_middleware(event: Event) -> Event | None:
    logger.debug(
        "event through middleware",
        extra={"event": event.name, "source": event.source, "id": event.id},
    )
    return event
