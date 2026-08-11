"""Security Gate — ponto único de decisão."""

from __future__ import annotations

import logging

from app.security.constants import DecisionEffect, RiskLevel, DEFAULT_FAIL_CLOSED
from app.security.models.decision import AuthorizationRequest, SecurityDecision
from app.security.models.identity import Identity
from app.security.rbac import RBACEngine

logger = logging.getLogger(__name__)


class SecurityGate:
    """Autoridade de autorização.

    Fail-closed por padrão.
    """

    def __init__(self, rbac: RBACEngine, fail_closed: bool = DEFAULT_FAIL_CLOSED) -> None:
        self._rbac = rbac
        self.fail_closed = fail_closed
        self._emergency_lock = False

    @property
    def emergency_lock(self) -> bool:
        return self._emergency_lock

    def set_emergency_lock(self, locked: bool) -> None:
        self._emergency_lock = locked
        logger.warning("emergency lock changed", extra={"locked": locked})

    def authorize(
        self,
        identity: Identity | None,
        request: AuthorizationRequest,
    ) -> SecurityDecision:
        if self._emergency_lock:
            return SecurityDecision(
                effect=DecisionEffect.DENY,
                request_id=request.id,
                reason="emergency lock active",
                risk=RiskLevel.CRITICAL,
                identity_id=request.identity_id,
                correlation_id=request.correlation_id,
            )

        if identity is None or not identity.active:
            return SecurityDecision(
                effect=DecisionEffect.DENY,
                request_id=request.id,
                reason="identity missing or inactive",
                risk=request.risk,
                identity_id=request.identity_id,
                correlation_id=request.correlation_id,
            )

        # Admin principal: amplo, mas ações CRITICAL ainda podem CHALLENGE
        if identity.is_admin:
            if request.risk == RiskLevel.CRITICAL:
                return SecurityDecision(
                    effect=DecisionEffect.CHALLENGE,
                    request_id=request.id,
                    reason="admin critical action requires challenge",
                    risk=request.risk,
                    identity_id=identity.id,
                    correlation_id=request.correlation_id,
                    policy_id="admin_critical_challenge",
                )
            return SecurityDecision(
                effect=DecisionEffect.ALLOW,
                request_id=request.id,
                reason="admin allow",
                risk=request.risk,
                identity_id=identity.id,
                correlation_id=request.correlation_id,
                policy_id="admin_allow",
            )

        allowed = self._rbac.is_allowed(identity, request.resource, request.action)
        if allowed:
            if request.risk in {RiskLevel.HIGH, RiskLevel.CRITICAL}:
                return SecurityDecision(
                    effect=DecisionEffect.CHALLENGE,
                    request_id=request.id,
                    reason="high risk requires challenge",
                    risk=request.risk,
                    identity_id=identity.id,
                    correlation_id=request.correlation_id,
                    policy_id="risk_challenge",
                )
            return SecurityDecision(
                effect=DecisionEffect.ALLOW,
                request_id=request.id,
                reason="rbac allow",
                risk=request.risk,
                identity_id=identity.id,
                correlation_id=request.correlation_id,
                policy_id="rbac_allow",
            )

        # fail-closed
        return SecurityDecision(
            effect=DecisionEffect.DENY,
            request_id=request.id,
            reason="rbac deny" if self.fail_closed else "rbac deny (fail-closed)",
            risk=request.risk,
            identity_id=identity.id,
            correlation_id=request.correlation_id,
            policy_id="rbac_deny",
        )
