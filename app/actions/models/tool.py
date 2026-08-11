"""Tool e capabilities."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable
import time

from app.actions.constants import RiskLevel, ToolCategory


@dataclass(slots=True)
class ToolCapabilities:
    dry_run: bool = True
    cancellable: bool = True
    idempotent: bool = False
    requires_confirmation: bool = False
    side_effects: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "dry_run": self.dry_run,
            "cancellable": self.cancellable,
            "idempotent": self.idempotent,
            "requires_confirmation": self.requires_confirmation,
            "side_effects": self.side_effects,
        }


@dataclass(slots=True)
class Tool:
    id: str
    name: str
    description: str = ""
    category: ToolCategory = ToolCategory.CUSTOM
    risk: RiskLevel = RiskLevel.LOW
    capabilities: ToolCapabilities = field(default_factory=ToolCapabilities)
    parameters_schema: dict[str, Any] = field(default_factory=dict)
    enabled: bool = True
    version: str = "1.0.0"
    handler: Callable[..., Any] | None = field(default=None, repr=False)
    created_at: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category": self.category.value,
            "risk": self.risk.value,
            "capabilities": self.capabilities.to_dict(),
            "parameters_schema": self.parameters_schema,
            "enabled": self.enabled,
            "version": self.version,
            "metadata": self.metadata,
        }
