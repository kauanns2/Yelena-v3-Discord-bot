"""Security session."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
import time
import uuid


@dataclass(slots=True)
class SecuritySession:
    identity_id: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    active: bool = True
    created_at: float = field(default_factory=time.time)
    expires_at: float | None = None
    last_seen: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def is_expired(self) -> bool:
        return self.expires_at is not None and time.time() > self.expires_at

    def touch(self) -> None:
        self.last_seen = time.time()

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "identity_id": self.identity_id,
            "active": self.active,
            "created_at": self.created_at,
            "expires_at": self.expires_at,
            "last_seen": self.last_seen,
            "metadata": self.metadata,
        }
