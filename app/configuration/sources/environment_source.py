"""Fonte de variáveis de ambiente.

Mapeia YELENA_* para seções de config.
Secrets (YELENA_SECRET_*) vão para o SecretStore, não para config pública.
"""

from __future__ import annotations

import os
from typing import Any

from app.configuration.constants import ConfigSourceType
from app.configuration.sources.base import ConfigSource

PREFIX = "YELENA_"
SECRET_PREFIX = "YELENA_SECRET_"


def _parse_value(raw: str) -> Any:
    lower = raw.lower()
    if lower in {"true", "1", "yes"}:
        return True
    if lower in {"false", "0", "no"}:
        return False
    try:
        if "." in raw:
            return float(raw)
        return int(raw)
    except ValueError:
        return raw


class EnvironmentSource(ConfigSource):
    @property
    def source_type(self) -> ConfigSourceType:
        return ConfigSourceType.ENVIRONMENT

    def load(self) -> dict[str, Any]:
        """Retorna apenas config pública. Secrets são separados."""
        result: dict[str, Any] = {}
        for key, value in os.environ.items():
            if not key.startswith(PREFIX):
                continue
            if key.startswith(SECRET_PREFIX):
                continue  # secrets tratados à parte

            # YELENA_APPLICATION_DEBUG -> application.debug
            path = key[len(PREFIX):].lower().split("_", 1)
            if len(path) == 1:
                result.setdefault("_root", {})[path[0]] = _parse_value(value)
            else:
                section, rest = path[0], path[1]
                result.setdefault(section, {})[rest] = _parse_value(value)
        return result

    def load_secrets(self) -> dict[str, str]:
        secrets: dict[str, str] = {}
        for key, value in os.environ.items():
            if key.startswith(SECRET_PREFIX):
                secret_key = key[len(SECRET_PREFIX):].lower()
                secrets[secret_key] = value
        return secrets
