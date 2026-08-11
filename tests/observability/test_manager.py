"""Testes do Observability Manager."""

from app.observability import ObservabilityManager
from app.observability.constants import HealthStatus, LogLevel


def test_start_and_metrics():
    obs = ObservabilityManager()
    obs.start()
    obs.metrics.incr("test_counter")
    assert obs.metrics.get_counter("test_counter") == 1


def test_health_aggregation():
    obs = ObservabilityManager()
    obs.start()
    obs.register_health("core", lambda: {"status": "healthy"})
    obs.register_health("memory", lambda: {"status": "degraded", "message": "high load"})
    report = obs.check_health()
    assert report.status == HealthStatus.DEGRADED


def test_log_redaction():
    obs = ObservabilityManager()
    obs.start()
    record = obs.logs.info("login", api_key="supersecret", user="kauan")
    assert record.fields["api_key"] == "********"
    assert record.fields["user"] == "kauan"


def test_diagnose():
    obs = ObservabilityManager()
    obs.start()
    obs.register_health("core", lambda: {"status": "healthy"})
    report = obs.diagnose()
    assert report.summary
    assert report.findings


def test_alert_cooldown():
    obs = ObservabilityManager()
    obs.start()
    a1 = obs.alerts.fire("disk", message="low", source="sys", fingerprint="disk")
    a2 = obs.alerts.fire("disk", message="low", source="sys", fingerprint="disk")
    assert a1 is not None
    assert a2 is None  # cooldown
