"""Validação de configuração."""

from __future__ import annotations

from typing import Any

from app.configuration.constants import Environment
from app.configuration.errors import ConfigValidationError
from app.configuration.models.config import YelenaConfig


def validate_config(config: YelenaConfig) -> None:
    errors: list[str] = []

    env = config.application.environment
    valid_envs = {e.value for e in Environment}
    if env not in valid_envs:
        errors.append(f"Invalid environment: {env}")

    if config.core.shutdown_timeout <= 0:
        errors.append("core.shutdown_timeout must be > 0")

    if config.core.health_timeout <= 0:
        errors.append("core.health_timeout must be > 0")

    if config.ai.max_tokens < 1:
        errors.append("ai.max_tokens must be >= 1")

    if not 0.0 <= config.ai.temperature <= 2.0:
        errors.append("ai.temperature must be between 0.0 and 2.0")

    if config.memory.max_retrieval < 1:
        errors.append("memory.max_retrieval must be >= 1")

    if config.neural.max_hops < 1:
        errors.append("neural.max_hops must be >= 1")

    # Produção: regras mais rígidas
    if env == Environment.PRODUCTION.value:
        if config.application.debug:
            errors.append("debug must be False in production")
        if not config.security.fail_closed:
            errors.append("security.fail_closed must be True in production")

    if errors:
        raise ConfigValidationError(
            "Configuration validation failed",
            context={"errors": errors},
        )
