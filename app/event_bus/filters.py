"""Filtros de eventos."""

from __future__ import annotations

from typing import Callable

from app.event_bus.models.event import Event

EventFilter = Callable[[Event], bool]


def by_name(name: str) -> EventFilter:
    def _filter(event: Event) -> bool:
        if name == "*":
            return True
        if name.endswith(".*"):
            return event.name.startswith(name[:-1])
        return event.name == name

    return _filter


def by_source(source: str) -> EventFilter:
    def _filter(event: Event) -> bool:
        return event.source == source

    return _filter


def by_priority_min(min_priority: int) -> EventFilter:
    def _filter(event: Event) -> bool:
        return event.priority.value >= min_priority

    return _filter


def combine(*filters: EventFilter) -> EventFilter:
    def _filter(event: Event) -> bool:
        return all(f(event) for f in filters)

    return _filter
