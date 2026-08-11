"""Dispatcher de eventos para subscribers."""

from __future__ import annotations

import logging
from typing import Any

from app.event_bus.constants import EventStatus
from app.event_bus.models.event import Event
from app.event_bus.models.subscription import Subscription

logger = logging.getLogger(__name__)


class Dispatcher:
    """Entrega eventos às subscriptions correspondentes."""

    def __init__(self) -> None:
        self._metrics = {
            "dispatched": 0,
            "handler_errors": 0,
            "no_subscribers": 0,
        }

    def dispatch(self, event: Event, subscriptions: list[Subscription]) -> dict[str, Any]:
        matched = [s for s in subscriptions if s.matches(event)]
        if not matched:
            self._metrics["no_subscribers"] += 1
            event.status = EventStatus.DELIVERED
            return {"delivered": 0, "errors": 0}

        event.status = EventStatus.DISPATCHING
        errors = 0
        delivered = 0

        # prioridade: handlers de eventos CRITICAL primeiro (já filtrados)
        for sub in matched:
            try:
                sub.handler(event)
                delivered += 1
            except Exception:
                errors += 1
                self._metrics["handler_errors"] += 1
                logger.exception(
                    "handler failed",
                    extra={"event": event.name, "subscription": sub.id},
                )

        event.status = EventStatus.FAILED if errors and not delivered else EventStatus.DELIVERED
        self._metrics["dispatched"] += 1
        return {"delivered": delivered, "errors": errors}

    @property
    def metrics(self) -> dict[str, int]:
        return dict(self._metrics)
