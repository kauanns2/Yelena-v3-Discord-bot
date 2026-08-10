"""Schemas de seções de configuração."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ApplicationConfig:
    name: str = "Yelena"
    version: str = "3.0.0-dev"
    environment: str = "development"
    debug: bool = False
    timezone: str = "UTC"
    locale: str = "pt-BR"

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "environment": self.environment,
            "debug": self.debug,
            "timezone": self.timezone,
            "locale": self.locale,
        }


@dataclass(slots=True)
class CoreConfig:
    shutdown_timeout: float = 30.0
    health_timeout: float = 5.0
    bootstrap_strict: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "shutdown_timeout": self.shutdown_timeout,
            "health_timeout": self.health_timeout,
            "bootstrap_strict": self.bootstrap_strict,
        }


@dataclass(slots=True)
class SecurityConfig:
    fail_closed: bool = True
    require_auth: bool = True
    session_timeout: float = 3600.0
    rate_limit_enabled: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "fail_closed": self.fail_closed,
            "require_auth": self.require_auth,
            "session_timeout": self.session_timeout,
            "rate_limit_enabled": self.rate_limit_enabled,
        }


@dataclass(slots=True)
class LoggingConfig:
    level: str = "INFO"
    json_format: bool = False
    redact_secrets: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "level": self.level,
            "json_format": self.json_format,
            "redact_secrets": self.redact_secrets,
        }


@dataclass(slots=True)
class DiscordConfig:
    """Schema apenas — implementação no módulo Discord."""

    enabled: bool = False
    command_prefix: str = "!"
    # token fica em secrets, nunca aqui em texto

    def to_dict(self) -> dict[str, Any]:
        return {
            "enabled": self.enabled,
            "command_prefix": self.command_prefix,
        }


@dataclass(slots=True)
class AIConfig:
    """Schema apenas — implementação no módulo AI Providers."""

    default_provider: str = ""
    default_model: str = ""
    max_tokens: int = 4096
    temperature: float = 0.7

    def to_dict(self) -> dict[str, Any]:
        return {
            "default_provider": self.default_provider,
            "default_model": self.default_model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
        }


@dataclass(slots=True)
class MemoryConfig:
    working_ttl_seconds: float = 1800.0
    max_retrieval: int = 20
    enable_decay: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "working_ttl_seconds": self.working_ttl_seconds,
            "max_retrieval": self.max_retrieval,
            "enable_decay": self.enable_decay,
        }


@dataclass(slots=True)
class NeuralConfig:
    enabled: bool = True
    max_hops: int = 8
    default_ttl: float = 30.0
    max_queue_size: int = 1000

    def to_dict(self) -> dict[str, Any]:
        return {
            "enabled": self.enabled,
            "max_hops": self.max_hops,
            "default_ttl": self.default_ttl,
            "max_queue_size": self.max_queue_size,
        }
