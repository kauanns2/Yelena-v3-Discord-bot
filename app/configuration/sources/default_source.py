"""Fonte de defaults seguros."""

from __future__ import annotations

from typing import Any

from app.configuration.constants import ConfigSourceType, Environment
from app.configuration.defaults import get_defaults
from app.configuration.sources.base import ConfigSource


class DefaultSource(ConfigSource):
    def __init__(self, environment: str = Environment.DEVELOPMENT.value) -> None:
        self._environment = environment

    @property
    def source_type(self) -> ConfigSourceType:
        return ConfigSourceType.DEFAULT

    def load(self) -> dict[str, Any]:
        return get_defaults(self._environment)
