"""Modelo formal de módulo e dependência."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.core.constants import LifecycleState, ModulePriority, HealthStatus


@dataclass(slots=True)
class ModuleDependency:
    """Dependência de um módulo."""

    module_id: str
    optional: bool = False
    min_version: str | None = None
    max_version: str | None = None
    reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "module_id": self.module_id,
            "optional": self.optional,
            "min_version": self.min_version,
            "max_version": self.max_version,
            "reason": self.reason,
        }


@dataclass(slots=True)
class ModuleInfo:
    """Representação formal de um módulo no Core."""

    id: str
    name: str
    version: str = "0.1.0"
    description: str = ""
    state: LifecycleState = LifecycleState.CREATED
    dependencies: list[ModuleDependency] = field(default_factory=list)
    optional_dependencies: list[ModuleDependency] = field(default_factory=list)
    priority: ModulePriority = ModulePriority.NORMAL
    health_status: HealthStatus = HealthStatus.UNKNOWN
    metadata: dict[str, Any] = field(default_factory=dict)
    instance: Any = field(default=None, repr=False)

    def __post_init__(self) -> None:
        if not self.id or not self.id.strip():
            raise ValueError("module id cannot be empty")
        self.id = self.id.strip().lower()

    @property
    def is_running(self) -> bool:
        return self.state in {LifecycleState.RUNNING, LifecycleState.DEGRADED}

    @property
    def all_dependencies(self) -> list[ModuleDependency]:
        return [*self.dependencies, *self.optional_dependencies]

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "state": self.state.value,
            "dependencies": [d.to_dict() for d in self.dependencies],
            "optional_dependencies": [d.to_dict() for d in self.optional_dependencies],
            "priority": self.priority.value,
            "health_status": self.health_status.value,
            "metadata": self.metadata,
        }
