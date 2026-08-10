"""Configuration Manager — ponto central de acesso à config."""

from __future__ import annotations

import logging
from typing import Any

from app.configuration.constants import Environment
from app.configuration.errors import ConfigurationError
from app.configuration.models.config import YelenaConfig
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
from app.configuration.resolver import ConfigResolver
from app.configuration.secrets import SecretStore
from app.configuration.sources.default_source import DefaultSource
from app.configuration.sources.environment_source import EnvironmentSource
from app.configuration.sources.memory_source import MemorySource
from app.configuration.validator import validate_config

logger = logging.getLogger(__name__)


def _build_section(cls: type, data: dict[str, Any]) -> Any:
    valid_fields = {f.name for f in cls.__dataclass_fields__.values()}  # type: ignore[attr-defined]
    filtered = {k: v for k, v in data.items() if k in valid_fields}
    return cls(**filtered)


class ConfigurationManager:
    """Carrega, valida e fornece configuração tipada.

    Nenhum módulo deve acessar os.environ diretamente.
    """

    def __init__(self, environment: str | None = None) -> None:
        self._environment = environment or Environment.DEVELOPMENT.value
        self._resolver = ConfigResolver()
        self._secrets = SecretStore()
        self._memory_source = MemorySource()
        self._config: YelenaConfig | None = None

    @property
    def config(self) -> YelenaConfig:
        if self._config is None:
            raise ConfigurationError("Configuration not loaded. Call load() first.")
        return self._config

    @property
    def is_loaded(self) -> bool:
        return self._config is not None

    def load(self) -> YelenaConfig:
        default_source = DefaultSource(self._environment)
        env_source = EnvironmentSource()

        sources = [default_source, env_source, self._memory_source]
        merged = self._resolver.resolve(sources)

        # Secrets do ambiente
        for key, value in env_source.load_secrets().items():
            self._secrets.set(key, value)

        config = YelenaConfig(
            application=_build_section(ApplicationConfig, merged.get("application", {})),
            core=_build_section(CoreConfig, merged.get("core", {})),
            security=_build_section(SecurityConfig, merged.get("security", {})),
            logging=_build_section(LoggingConfig, merged.get("logging", {})),
            discord=_build_section(DiscordConfig, merged.get("discord", {})),
            ai=_build_section(AIConfig, merged.get("ai", {})),
            memory=_build_section(MemoryConfig, merged.get("memory", {})),
            neural=_build_section(NeuralConfig, merged.get("neural", {})),
        )

        # Sincronizar environment
        if self._environment:
            config.application.environment = self._environment

        # Copiar secrets para o objeto (acesso controlado)
        for key in self._secrets.keys():
            val = self._secrets.get(key)
            if val is not None:
                config.set_secret(key, val)

        validate_config(config)
        self._config = config

        logger.info(
            "configuration loaded",
            extra={
                "environment": config.application.environment,
                "sections": list(config.to_dict().keys()),
            },
        )
        return config

    def override(self, section: str, key: str, value: Any) -> None:
        """Override em memória (testes / runtime controlado)."""
        if self._config and self._config.application.environment == Environment.PRODUCTION.value:
            # Em produção, overrides são restritos
            logger.warning("runtime override in production", extra={"section": section, "key": key})

        self._memory_source.set(section, key, value)
        self.load()  # reload com novo override

    def get_secret(self, key: str) -> str | None:
        return self._secrets.get(key)

    def require_secret(self, key: str) -> str:
        return self._secrets.require(key)

    def masked_snapshot(self) -> dict[str, Any]:
        if self._config is None:
            return {}
        return self._config.masked_dict()
