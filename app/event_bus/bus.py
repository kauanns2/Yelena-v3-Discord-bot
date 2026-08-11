"""Event Bus — publicação e assinatura de eventos."""

from __future__ import annotations

import logging
import time
from typing import Any, Callable

from app.event_bus.constants import (
    EventPriority,
    EventStatus,
    DEFAULT_MAX_QUEUE,
    DEFAULT_TTL,
)
from app.event_bus.dispatcher import Dispatcher
from app.event_bus.errors import EventValidationError, EventExpiredError, QueueFullError
from app.event_bus.middleware import MiddlewarePipeline, ttl_middleware
from app.event_bus.models.event import Event
from app.event_bus.models.subscription import Subscription
from app.event_bus.types import SubscriptionId

logger = logging.getLogger(__name__)


class EventBus:
    """Bus de eventos formal da Yelena.

    Produtores não conhecem consumidores.
    """

    def __init__(self, max_queue: int = DEFAULT_MAX_QUEUE) -> None:
        self._subscriptions: dict[SubscriptionId, Subscription] = {}
        self._dispatcher = Dispatcher()
        self._middleware = MiddlewarePipeline()
        self._middleware.use(ttl_middleware)
        self._max_queue = max_queue
        self._recent_ids: dict[str, float] = {}  # dedup simples
        self._dedup_ttl = 30.0
        self._started = False
        self._metrics = {
            "published": 0,
            "dropped_expired": 0,
            "dropped_duplicate": 0,
            "dropped_queue_full": 0,
        }

    @property
    def is_started(self) -> bool:
        return self._started

    def start(self) -> None:
        self._started = True
        logger.info("event bus started")

    def stop(self) -> None:
        self._started = False
        logger.info("event bus stopped")

    def use(self, middleware: Callable[[Event], Event | None]) -> None:
        self._middleware.use(middleware)

    def subscribe(
        self,
        event_name: str,
        handler: Callable[..., Any],
        *,
        source_filter: str | None = None,
        priority_min: int | None = None,
    ) -> SubscriptionId:
        sub = Subscription(
            event_name=event_name,
            handler=handler,
            source_filter=source_filter,
            priority_min=priority_min,
        )
        self._subscriptions[sub.id] = sub
        logger.debug(
            "subscribed",
            extra={"event": event_name, "subscription_id": sub.id},
        )
        return sub.id

    def unsubscribe(self, subscription_id: SubscriptionId) -> bool:
        removed = self._subscriptions.pop(subscription_id, None)
        return removed is not None

    def publish(
        self,
        name: str,
        payload: dict[str, Any] | None = None,
        *,
        source: str = "",
        priority: EventPriority = EventPriority.NORMAL,
        correlation_id: str | None = None,
        causation_id: str | None = None,
        trace_id: str | None = None,
        ttl: float = DEFAULT_TTL,
        metadata: dict[str, Any] | None = None,
    ) -> Event:
        event = Event(
            name=name,
            payload=payload or {},
            source=source,
            priority=priority,
            correlation_id=correlation_id,
            causation_id=causation_id,
            trace_id=trace_id,
            ttl=ttl,
            metadata=metadata or {},
        )
        return self.publish_event(event)

    def publish_event(self, event: Event) -> Event:
        if not event.name:
            raise EventValidationError("Event name is required")

        # dedup
        self._purge_dedup()
        if event.id in self._recent_ids:
            self._metrics["dropped_duplicate"] += 1
            event.status = EventStatus.DELIVERED
            return event

        if len(self._recent_ids) >= self._max_queue:
            self._metrics["dropped_queue_full"] += 1
            raise QueueFullError("Event bus dedup queue is full")

        processed = self._middleware.run(event)
        if processed is None:
            self._metrics["dropped_expired"] += 1
            event.status = EventStatus.EXPIRED
            return event

        result = self._dispatcher.dispatch(processed, list(self._subscriptions.values()))
        self._recent_ids[event.id] = time.time()
        self._metrics["published"] += 1

        logger.debug(
            "event published",
            extra={
                "event": event.name,
                "id": event.id,
                "delivered": result["delivered"],
                "errors": result["errors"],
            },
        )
        return event

    def _purge_dedup(self) -> None:
        now = time.time()
        expired = [k for k, ts in self._recent_ids.items() if now - ts > self._dedup_ttl]
        for k in expired:
            del self._recent_ids[k]

    def list_subscriptions(self, event_name: str | None = None) -> list[Subscription]:
        subs = list(self._subscriptions.values())
        if event_name:
            return [s for s in subs if s.event_name == event_name or s.event_name == "*"]
        return subs

    def health(self) -> dict[str, Any]:
        return {
            "status": "healthy" if self._started else "stopped",
            "subscriptions": len(self._subscriptions),
            "metrics": {**self._metrics, **self._dispatcher.metrics},
        }
