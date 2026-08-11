"""Testes do Event Bus."""

import pytest

from app.event_bus import EventBus, Event
from app.event_bus.constants import EventPriority, EventStatus
from app.event_bus.errors import EventValidationError


def test_publish_subscribe():
    bus = EventBus()
    bus.start()
    received = []

    bus.subscribe("test.event", lambda e: received.append(e.payload))
    bus.publish("test.event", payload={"ok": True}, source="test")

    assert received == [{"ok": True}]


def test_unsubscribe():
    bus = EventBus()
    received = []
    sub_id = bus.subscribe("test.event", lambda e: received.append(1))
    bus.unsubscribe(sub_id)
    bus.publish("test.event", payload={})
    assert received == []


def test_wildcard_subscription():
    bus = EventBus()
    received = []
    bus.subscribe("memory.*", lambda e: received.append(e.name))
    bus.publish("memory.recalled", payload={})
    bus.publish("memory.stored", payload={})
    bus.publish("emotion.changed", payload={})
    assert "memory.recalled" in received
    assert "memory.stored" in received
    assert "emotion.changed" not in received


def test_source_filter():
    bus = EventBus()
    received = []
    bus.subscribe("test.event", lambda e: received.append(e.source), source_filter="memory")
    bus.publish("test.event", source="memory")
    bus.publish("test.event", source="emotion")
    assert received == ["memory"]


def test_expired_event_dropped():
    bus = EventBus()
    received = []
    bus.subscribe("test.event", lambda e: received.append(1))
    event = Event(name="test.event", ttl=0.0)
    event.created_at = 0.0
    result = bus.publish_event(event)
    assert result.status == EventStatus.EXPIRED
    assert received == []


def test_correlation_id():
    bus = EventBus()
    seen = []
    bus.subscribe("test.event", lambda e: seen.append(e.correlation_id))
    bus.publish("test.event", correlation_id="abc-123")
    assert seen == ["abc-123"]
