"""Testes do Security Manager."""

from app.security import SecurityManager
from app.security.constants import DecisionEffect, RiskLevel, IdentityType
from app.security.models.identity import Identity


def test_admin_allow():
    sec = SecurityManager(admin_id="admin")
    sec.start()
    d = sec.authorize("admin", "action", "execute", risk=RiskLevel.LOW)
    assert d.effect == DecisionEffect.ALLOW


def test_admin_critical_challenge():
    sec = SecurityManager()
    sec.start()
    d = sec.authorize("admin", "system", "destroy", risk=RiskLevel.CRITICAL)
    assert d.effect == DecisionEffect.CHALLENGE


def test_unknown_identity_deny():
    sec = SecurityManager()
    sec.start()
    d = sec.authorize("unknown", "memory", "read")
    assert d.effect == DecisionEffect.DENY


def test_user_role():
    sec = SecurityManager()
    sec.start()
    sec.register_identity(
        Identity(id="user1", identity_type=IdentityType.USER, roles=["user"])
    )
    d = sec.authorize("user1", "memory", "read")
    assert d.effect == DecisionEffect.ALLOW
    d2 = sec.authorize("user1", "config", "write")
    assert d2.effect == DecisionEffect.DENY


def test_emergency_lock():
    sec = SecurityManager()
    sec.start()
    sec.gate.set_emergency_lock(True)
    d = sec.authorize("admin", "action", "execute")
    assert d.effect == DecisionEffect.DENY


def test_audit_records():
    sec = SecurityManager()
    sec.start()
    sec.authorize("admin", "action", "execute")
    assert len(sec.audit) >= 1
