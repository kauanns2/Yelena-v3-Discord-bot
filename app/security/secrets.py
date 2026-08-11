"""Secret references — nunca logar valor."""

from __future__ import annotations

from app.security.errors import SecretError


class SecretStore:
    """Armazena secrets em memória. Valores nunca vão para audit/logs."""

    def __init__(self) -> None:
        self._secrets: dict[str, str] = {}

    def set(self, key: str, value: str) -> None:
        if not key or value is None:
            raise SecretError("Secret key and value required")
        self._secrets[key] = value

    def get(self, key: str) -> str | None:
        return self._secrets.get(key)

    def require(self, key: str) -> str:
        value = self.get(key)
        if value is None:
            raise SecretError(f"Secret not found: {key}", context={"key": key})
        return value

    def has(self, key: str) -> bool:
        return key in self._secrets

    def keys(self) -> list[str]:
        return list(self._secrets.keys())

    def redact(self, key: str) -> str:
        return f"secret:{key}" if key in self._secrets else f"secret:{key}:missing"
