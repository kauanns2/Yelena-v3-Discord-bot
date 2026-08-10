"""Metadados estruturados da aplicação."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.core.version import YELENA_VERSION, CORE_VERSION


@dataclass(frozen=True, slots=True)
class ApplicationMetadata:
    """Metadados imutáveis da aplicação."""

    name: str = "Yelena"
    codename: str = "V3"
    version: str = YELENA_VERSION
    core_version: str = CORE_VERSION
    description: str = (
        "Plataforma modular de IA com identidade, personalidade, "
        "memória, raciocínio e segurança arquitetural."
    )
    architecture: str = "modular-neural-web"
    environment: str = "development"
    extra: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "codename": self.codename,
            "version": self.version,
            "core_version": self.core_version,
            "description": self.description,
            "architecture": self.architecture,
            "environment": self.environment,
            **self.extra,
        }
