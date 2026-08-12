"""Adapters de plataforma."""

from app.bridge.platforms.base import PlatformAdapter, InboundMessage, OutboundMessage
from app.bridge.platforms.registry import PlatformRegistry

__all__ = [
    "PlatformAdapter",
    "InboundMessage",
    "OutboundMessage",
    "PlatformRegistry",
]
