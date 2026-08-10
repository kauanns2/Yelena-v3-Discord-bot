"""Gerenciador de estado global do Core."""

from __future__ import annotations

import time
from typing import Any

from app.core.constants import LifecycleState, HealthStatus
from app.core.models.state import CoreState


class StateManager:
    """Mantém o estado global tipado e controlado do Core."""

    def __init__(self) -> None:
        self._state = CoreState()

    @property
    def state(self) -> CoreState:
        return self._state

    def set_lifecycle(self, lifecycle: LifecycleState) -> None:
        self._state.lifecycle = lifecycle
        if lifecycle == LifecycleState.RUNNING and self._state.started_at is None:
            self._state.started_at = time.time()
        if lifecycle in {LifecycleState.STOPPED, LifecycleState.FAILED}:
            self._state.stopped_at = time.time()

    def set_health(self, health: HealthStatus) -> None:
        self._state.health = health

    def set_environment(self, environment: str) -> None:
        self._state.environment = environment

    def set_correlation_id(self, correlation_id: str | None) -> None:
        self._state.correlation_id = correlation_id

    def add_error(self, error: str) -> None:
        self._state.errors.append(error)

    def clear_errors(self) -> None:
        self._state.errors.clear()

    def update_metadata(self, key: str, value: Any) -> None:
        self._state.metadata[key] = value

    def snapshot(self) -> dict[str, Any]:
        return self._state.to_dict()
