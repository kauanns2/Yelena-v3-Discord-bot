"""RBAC engine simples."""

from __future__ import annotations

from app.security.models.identity import Identity
from app.security.models.permission import Permission, Role


class RBACEngine:
    def __init__(self) -> None:
        self.roles: dict[str, Role] = {}
        self.permissions: dict[str, Permission] = {}
        self._seed_defaults()

    def _seed_defaults(self) -> None:
        self.permissions["*:*"] = Permission(id="*:*", resource="*", action="*", description="full access")
        self.permissions["action:execute"] = Permission(
            id="action:execute", resource="action", action="execute"
        )
        self.permissions["action:read"] = Permission(
            id="action:read", resource="action", action="read"
        )
        self.permissions["memory:read"] = Permission(
            id="memory:read", resource="memory", action="read"
        )
        self.permissions["memory:write"] = Permission(
            id="memory:write", resource="memory", action="write"
        )
        self.permissions["config:read"] = Permission(
            id="config:read", resource="config", action="read"
        )
        self.permissions["config:write"] = Permission(
            id="config:write", resource="config", action="write"
        )

        self.roles["admin"] = Role(
            id="admin",
            permissions=["*:*"],
            description="Administrator principal",
        )
        self.roles["user"] = Role(
            id="user",
            permissions=["action:read", "memory:read", "config:read"],
            description="Usuário padrão",
        )
        self.roles["system"] = Role(
            id="system",
            permissions=["*:*"],
            description="Sistema interno",
        )

    def identity_permissions(self, identity: Identity) -> set[str]:
        perms = set(identity.permissions)
        for role_id in identity.roles:
            role = self.roles.get(role_id)
            if role:
                perms.update(role.permissions)
        return perms

    def is_allowed(self, identity: Identity, resource: str, action: str) -> bool:
        if not identity.active:
            return False
        perm_ids = self.identity_permissions(identity)
        for pid in perm_ids:
            perm = self.permissions.get(pid)
            if perm and perm.matches(resource, action):
                return True
            # wildcard shorthand
            if pid == "*:*":
                return True
            if pid == f"{resource}:*" or pid == f"*:{action}" or pid == f"{resource}:{action}":
                return True
        return False
