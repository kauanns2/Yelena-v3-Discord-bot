"""Security Manager."""

from __future__ import annotations

import logging
import time
from typing import Any

from app.security.audit import AuditLog
from app.security.constants import IdentityType, RiskLevel, DecisionEffect, DEFAULT_ADMIN_ID
from app.security.gate import SecurityGate
from app.security.models.decision import AuthorizationRequest, SecurityDecision
from app.security.models.identity import Identity
from app.security.models.session import SecuritySession
from app.security.rbac import RBACEngine
from app.security.secrets import SecretStore

logger = logging.getLogger(__name__)


class SecurityManager:
    """API principal de segurança.

    Você (admin) é o administrador principal.
    Yelena pode questionar, mas não remove sua autoridade.
    """

    def __init__(self, admin_id: str = DEFAULT_ADMIN_ID) -> None:
        self._rbac = RBACEngine()
        self.gate = SecurityGate(self._rbac)
        self.audit = AuditLog()
        self.secrets = SecretStore()
        self._identities: dict[str, Identity] = {}
        self._sessions: dict[str, SecuritySession] = {}
        self._started = False
        self._admin_id = admin_id
        self._metrics = {
            "authorizations": 0,
            "allows": 0,
            "denies": 0,
            "challenges": 0,
        }
        self._seed_identities()

    def _seed_identities(self) -> None:
        admin = Identity(
            id=self._admin_id,
            identity_type=IdentityType.ADMIN,
            name="Administrator",
            roles=["admin"],
            trusted=True,
        )
        system = Identity(
            id="system",
            identity_type=IdentityType.SYSTEM,
            name="Yelena System",
            roles=["system"],
            trusted=True,
        )
        self._identities[admin.id] = admin
        self._identities[system.id] = system

    @property
    def is_started(self) -> bool:
        return self._started

    def start(self) -> None:
        self._started = True
        logger.info("security system started", extra={"admin_id": self._admin_id})

    def stop(self) -> None:
        self._started = False

    def register_identity(self, identity: Identity) -> None:
        self._identities[identity.id] = identity

    def get_identity(self, identity_id: str) -> Identity | None:
        return self._identities.get(identity_id)

    def create_session(self, identity_id: str, ttl: float = 3600.0) -> SecuritySession:
        session = SecuritySession(
            identity_id=identity_id,
            expires_at=time.time() + ttl,
        )
        self._sessions[session.id] = session
        return session

    def authorize(
        self,
        identity_id: str,
        resource: str,
        action: str,
        *,
        risk: RiskLevel = RiskLevel.LOW,
        session_id: str | None = None,
        correlation_id: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> SecurityDecision:
        request = AuthorizationRequest(
            identity_id=identity_id,
            resource=resource,
            action=action,
            risk=risk,
            session_id=session_id,
            correlation_id=correlation_id,
            context=context or {},
        )
        identity = self.get_identity(identity_id)
        decision = self.gate.authorize(identity, request)
        self.audit.record_decision(request, decision)

        self._metrics["authorizations"] += 1
        if decision.effect == DecisionEffect.ALLOW:
            self._metrics["allows"] += 1
        elif decision.effect == DecisionEffect.DENY:
            self._metrics["denies"] += 1
        else:
            self._metrics["challenges"] += 1

        return decision

    def check_allowed(self, identity_id: str, resource: str, action: str, **kwargs: Any) -> bool:
        return self.authorize(identity_id, resource, action, **kwargs).allowed

    def health(self) -> dict[str, Any]:
        return {
            "status": "healthy" if self._started else "stopped",
            "identities": len(self._identities),
            "sessions": len(self._sessions),
            "audit_records": len(self.audit),
            "emergency_lock": self.gate.emergency_lock,
            "metrics": dict(self._metrics),
        }
