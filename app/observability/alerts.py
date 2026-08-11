"""Alert manager com cooldown."""

from __future__ import annotations

import time

from app.observability.constants import AlertSeverity, DEFAULT_ALERT_COOLDOWN
from app.observability.models.alert import Alert


class AlertManager:
    def __init__(self, cooldown: float = DEFAULT_ALERT_COOLDOWN) -> None:
        self._alerts: list[Alert] = []
        self._last_fired: dict[str, float] = {}
        self._cooldown = cooldown

    def fire(
        self,
        title: str,
        *,
        severity: AlertSeverity = AlertSeverity.WARNING,
        message: str = "",
        source: str = "",
        fingerprint: str | None = None,
    ) -> Alert | None:
        fp = fingerprint or f"{source}:{title}"
        now = time.time()
        last = self._last_fired.get(fp)
        if last is not None and now - last < self._cooldown:
            return None  # dedup / cooldown

        alert = Alert(
            title=title,
            severity=severity,
            message=message,
            source=source,
            fingerprint=fp,
        )
        self._alerts.append(alert)
        self._last_fired[fp] = now
        return alert

    def active(self) -> list[Alert]:
        return [a for a in self._alerts if a.active]

    def recent(self, n: int = 20) -> list[Alert]:
        return self._alerts[-n:]
