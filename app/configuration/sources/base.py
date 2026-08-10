"""Interface base de fonte de configuração."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from app.configuration.constants import ConfigSourceType


class ConfigSource(ABC):
    @property
    @abstractmethod
    def source_type(self) -> ConfigSourceType: ...

    @abstractmethod
    def load(self) -> dict[str, Any]: ...
