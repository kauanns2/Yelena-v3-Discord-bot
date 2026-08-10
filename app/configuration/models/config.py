"""Modelo central de configuração da Yelena."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.configuration.models.sections import (
    ApplicationConfig,
    CoreConfig,
    SecurityConfig,
    LoggingConfig,
    DiscordConfig,
    AIConfig,
    MemoryConfig,
    NeuralConfig,
)


@dataclass(slots=True)
class YelenaConfig:
    """Configuração efetiva agregada de todas as seções."""

    application: ApplicationConfig = field(default_factory=ApplicationConfig)
    core: CoreConfig = field(default_factory=CoreConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    discord: DiscordConfig = field(default_factory=DiscordConfig)
    ai: AIConfig = field(default_factory=AIConfig)
    memory: MemoryConfig = field(default_factory=MemoryConfig)
    neural: NeuralConfig = field(default_factory=NeuralConfig)
    # secrets nunca ficam no objeto público serializado
    _secrets: dict[str, str] = field(default_factory=dict, repr=False)

    def get_secret(self, key: str) -> str | None:
        return self._secrets.get(key)

    def set_secret(self, key: str, value: str) -> None:
        self._secrets[key] = value

    def to_dict(self, *, include_secrets: bool = False) -> dict[str, Any]:
        data = {
            "application": self.application.to_dict(),
            "core": self.core.to_dict(),
            "security": self.security.to_dict(),
            "logging": self.logging.to_dict(),
            "discord": self.discord.to_dict(),
            "ai": self.ai.to_dict(),
            "memory": self.memory.to_dict(),
            "neural": self.neural.to_dict(),
        }
        if include_secrets:
            # Nunca usar em logs — só para testes controlados
            data["_secrets_keys"] = list(self._secrets.keys())
        return data

    def masked_dict(self) -> dict[str, Any]:
        """Representação segura para logs."""
        data = self.to_dict()
        data["secrets"] = {k: "********" for k in self._secrets}
        return data
