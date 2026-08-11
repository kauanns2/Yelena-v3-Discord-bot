"""
Módulo 4 — Event Bus

Sistema formal de comunicação baseada em eventos entre componentes.
Não substitui a Neural Web (relações/sinais) nem o Core (lifecycle).
"""

from app.event_bus.bus import EventBus
from app.event_bus.models.event import Event
from app.event_bus.errors import EventBusError

__all__ = ["EventBus", "Event", "EventBusError"]
