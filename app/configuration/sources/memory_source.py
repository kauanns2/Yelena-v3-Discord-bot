"""Fonte em memória para overrides de runtime/testes."""

from __future__ import annotations

from typing import Any

from app.configuration.constants import ConfigSourceType
from app.configuration.sources.base import ConfigSource


class MemorySource(ConfigSource):
    def __init__(self) -> None:
        self._data: dict[str, Any] = {}

    @property
    def source_type(self) -> ConfigSourceType:
        return ConfigSourceType.MEMORY

    def load(self) -> dict[str, Any]:
        return dict(self._data)

    def set(self, section: str, key: str, value: Any) -> None:
        self._data.setdefault(section, {})[key] = value

    def set_section(self, section: str, data: dict[str, Any]) -> None:
        self._data[section] = dict(data)

    def clear(self) -> None:
        self._data.clear()
