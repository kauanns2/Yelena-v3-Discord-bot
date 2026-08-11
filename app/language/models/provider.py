"""Provider info e capabilities."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ProviderCapabilities:
    supports_streaming: bool = False
    supports_system_prompt: bool = True
    supports_structured_output: bool = False
    max_tokens: int = 4096
    languages: list[str] = field(default_factory=lambda: ["pt-BR", "en"])

    def to_dict(self) -> dict[str, Any]:
        return {
            "supports_streaming": self.supports_streaming,
            "supports_system_prompt": self.supports_system_prompt,
            "supports_structured_output": self.supports_structured_output,
            "max_tokens": self.max_tokens,
            "languages": list(self.languages),
        }


@dataclass(slots=True)
class ProviderInfo:
    id: str
    name: str
    capabilities: ProviderCapabilities = field(default_factory=ProviderCapabilities)
    enabled: bool = True
    priority: int = 50
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "capabilities": self.capabilities.to_dict(),
            "enabled": self.enabled,
            "priority": self.priority,
            "metadata": self.metadata,
        }
