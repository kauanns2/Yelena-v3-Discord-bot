"""Audit log append-only em memória."""

from __future__ import annotations

from app.security.models.audit import AuditRecord
from app.security.models.decision import SecurityDecision, AuthorizationRequest


class AuditLog:
    def __init__(self, max_records: int = 5000) -> None:
        self._records: list[AuditRecord] = []
        self._max = max_records

    def append(self, record: AuditRecord) -> None:
        self._records.append(record)
        if len(self._records) > self._max:
            self._records = self._records[-self._max :]

    def record_decision(
        self,
        request: AuthorizationRequest,
        decision: SecurityDecision,
    ) -> AuditRecord:
        record = AuditRecord(
            event="security.decision",
            identity_id=request.identity_id,
            resource=request.resource,
            action=request.action,
            effect=decision.effect.value,
            reason=decision.reason,
            correlation_id=request.correlation_id,
            metadata={"risk": request.risk.value, "policy_id": decision.policy_id},
        )
        self.append(record)
        return record

    def list_recent(self, n: int = 50) -> list[AuditRecord]:
        return self._records[-n:]

    def __len__(self) -> int:
        return len(self._records)
