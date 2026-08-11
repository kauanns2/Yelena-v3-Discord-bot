"""Identity model."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
import time

from app.security.constants import IdentityType


@dataclass(slots=True)
class Identity:
    id: str
    identity_type: IdentityType = IdentityType.USER
    name: str = ""
    roles: list[str] = field(default_factory=list)
    permissions: list[str] = field(default_factory=list)
    active: bool = True
    trusted: bool = False
    created_at: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def is_admin(self) -> bool:
        return (
            self.identity_type == IdentityType.ADMIN
            or "admin" in self.roles
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "identity_type": self.identity_type.value,
            "name": self.name,
            "roles": list(self.roles),
            "permissions": list(self.permissions),
            "active": self.active,
            "trusted": self.trusted,
            "created_at": self.created_at,
            "metadata": self.metadata,
        }
