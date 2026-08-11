"""AuthorizationRequest e SecurityDecision."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
import time
import uuid

from app.security.constants import DecisionEffect, RiskLevel


@dataclass(slots=True)
class AuthorizationRequest:
    identity_id: str
    resource: str
    action: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    risk: RiskLevel = RiskLevel.LOW
    session_id: str | None = None
    correlation_id: str | None = None
    context: dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "identity_id": self.identity_id,
            "resource": self.resource,
            "action": self.action,
            "risk": self.risk.value,
            "session_id": self.session_id,
            "correlation_id": self.correlation_id,
            "context": self.context,
            "created_at": self.created_at,
        }


@dataclass(slots=True)
class SecurityDecision:
    effect: DecisionEffect
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    request_id: str = ""
    reason: str = ""
    policy_id: str | None = None
    risk: RiskLevel = RiskLevel.LOW
    identity_id: str = ""
    correlation_id: str | None = None
    created_at: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def allowed(self) -> bool:
        return self.effect == DecisionEffect.ALLOW

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "effect": self.effect.value,
            "request_id": self.request_id,
            "reason": self.reason,
            "policy_id": self.policy_id,
            "risk": self.risk.value,
            "identity_id": self.identity_id,
            "correlation_id": self.correlation_id,
            "created_at": self.created_at,
            "metadata": self.metadata,
        }
