"""Eventos do Core — contratos para o futuro Event Bus."""

from app.core.events.system import SystemEvents
from app.core.events.module import ModuleEvents

__all__ = ["SystemEvents", "ModuleEvents"]
