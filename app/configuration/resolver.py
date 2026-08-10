"""Resolve precedência entre fontes de configuração."""

from __future__ import annotations

from typing import Any

from app.configuration.constants import SOURCE_PRIORITY, ConfigSourceType
from app.configuration.sources.base import ConfigSource


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    result = dict(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


class ConfigResolver:
    """Combina fontes na ordem de precedência."""

    def resolve(self, sources: list[ConfigSource]) -> dict[str, Any]:
        ordered = sorted(
            sources,
            key=lambda s: SOURCE_PRIORITY.get(s.source_type, 0),
        )
        merged: dict[str, Any] = {}
        for source in ordered:
            data = source.load()
            merged = deep_merge(merged, data)
        return merged
