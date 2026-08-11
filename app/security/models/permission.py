"""Permission e Role."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class Permission:
    id: str
    description: str = ""
    resource: str = "*"
    action: str = "*"

    def matches(self, resource: str, action: str) -> bool:
        resource_ok = self.resource == "*" or self.resource == resource or resource.startswith(self.resource.rstrip("*") )
        action_ok = self.action == "*" or self.action == action
        return resource_ok and action_ok

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "description": self.description,
            "resource": self.resource,
            "action": self.action,
        }


@dataclass(slots=True)
class Role:
    id: str
    permissions: list[str] = field(default_factory=list)
    description: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "permissions": list(self.permissions),
            "description": self.description,
        }
