"""Gestão e masking de secrets."""

from __future__ import annotations

import re
from typing import Any

from app.configuration.constants import SECRET_MASK
from app.configuration.errors import SecretError

SECRET_KEY_PATTERNS = re.compile(
    r"(token|secret|password|api_key|apikey|credential|private_key|auth)",
    re.IGNORECASE,
)


class SecretStore:
    """Armazena secrets separados da config pública."""

    def __init__(self) -> None:
        self._secrets: dict[str, str] = {}

    def set(self, key: str, value: str) -> None:
        if not key or not value:
            raise SecretError("Secret key and value are required")
        self._secrets[key] = value

    def get(self, key: str) -> str | None:
        return self._secrets.get(key)

    def require(self, key: str) -> str:
        value = self.get(key)
        if value is None:
            raise SecretError(
                f"Required secret missing: {key}",
                context={"key": key},
            )
        return value

    def has(self, key: str) -> bool:
        return key in self._secrets

    def keys(self) -> list[str]:
        return list(self._secrets.keys())

    def clear(self) -> None:
        self._secrets.clear()


def is_secret_key(key: str) -> bool:
    return bool(SECRET_KEY_PATTERNS.search(key))


def mask_value(value: str) -> str:
    if not value:
        return SECRET_MASK
    if len(value) <= 4:
        return SECRET_MASK
    return SECRET_MASK


def mask_dict(data: dict[str, Any]) -> dict[str, Any]:
    """Mascara valores de chaves sensíveis recursivamente."""
    result: dict[str, Any] = {}
    for key, value in data.items():
        if is_secret_key(key):
            result[key] = SECRET_MASK
        elif isinstance(value, dict):
            result[key] = mask_dict(value)
        else:
            result[key] = value
    return result
