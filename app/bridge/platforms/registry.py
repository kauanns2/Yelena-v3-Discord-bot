"""Registry de plataformas."""

from __future__ import annotations

from app.bridge.errors import PlatformError
from app.bridge.platforms.base import PlatformAdapter


class PlatformRegistry:
    def __init__(self) -> None:
        self._adapters: dict[str, PlatformAdapter] = {}

    def register(self, adapter: PlatformAdapter) -> None:
        self._adapters[adapter.platform_id] = adapter

    def get(self, platform_id: str) -> PlatformAdapter | None:
        return self._adapters.get(platform_id)

    def require(self, platform_id: str) -> PlatformAdapter:
        adapter = self.get(platform_id)
        if adapter is None:
            raise PlatformError(f"Platform not registered: {platform_id}")
        return adapter

    def list_ids(self) -> list[str]:
        return list(self._adapters.keys())
