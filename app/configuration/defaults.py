"""Valores padrão seguros."""

from __future__ import annotations

from typing import Any

from app.configuration.constants import Environment


def get_defaults(environment: str = Environment.DEVELOPMENT.value) -> dict[str, Any]:
    debug = environment == Environment.DEVELOPMENT.value
    log_level = "DEBUG" if debug else "INFO"

    return {
        "application": {
            "name": "Yelena",
            "version": "3.0.0-dev",
            "environment": environment,
            "debug": debug,
            "timezone": "UTC",
            "locale": "pt-BR",
        },
        "core": {
            "shutdown_timeout": 30.0,
            "health_timeout": 5.0,
            "bootstrap_strict": True,
        },
        "security": {
            "fail_closed": True,
            "require_auth": environment == Environment.PRODUCTION.value,
            "session_timeout": 3600.0,
            "rate_limit_enabled": True,
        },
        "logging": {
            "level": log_level,
            "json_format": environment == Environment.PRODUCTION.value,
            "redact_secrets": True,
        },
        "discord": {
            "enabled": False,
            "command_prefix": "!",
        },
        "ai": {
            "default_provider": "",
            "default_model": "",
            "max_tokens": 4096,
            "temperature": 0.7,
        },
        "memory": {
            "working_ttl_seconds": 1800.0,
            "max_retrieval": 20,
            "enable_decay": True,
        },
        "neural": {
            "enabled": True,
            "max_hops": 8,
            "default_ttl": 30.0,
            "max_queue_size": 1000,
        },
    }
