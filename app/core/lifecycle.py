"""Controle de ciclo de vida com transições validadas."""

from __future__ import annotations

import logging
from typing import Callable

from app.core.constants import LifecycleState, VALID_TRANSITIONS
from app.core.exceptions import LifecycleError
from app.core.models.lifecycle import LifecycleEvent

logger = logging.getLogger(__name__)


class LifecycleManager:
    """Gerencia estados e transições de lifecycle."""

    def __init__(self, source: str = "core") -> None:
        self._source = source
        self._state = LifecycleState.CREATED
        self._history: list[LifecycleEvent] = []
        self._listeners: list[Callable[[LifecycleEvent], None]] = []

    @property
    def state(self) -> LifecycleState:
        return self._state

    @property
    def history(self) -> list[LifecycleEvent]:
        return list(self._history)

    def can_transition(self, to_state: LifecycleState) -> bool:
        return to_state in VALID_TRANSITIONS.get(self._state, set())

    def transition(self, to_state: LifecycleState, reason: str = "") -> LifecycleEvent:
        if not self.can_transition(to_state):
            raise LifecycleError(
                f"Invalid transition: {self._state.value} -> {to_state.value}",
                context={
                    "source": self._source,
                    "from": self._state.value,
                    "to": to_state.value,
                },
            )

        event = LifecycleEvent(
            source=self._source,
            from_state=self._state,
            to_state=to_state,
            reason=reason,
        )
        self._state = to_state
        self._history.append(event)

        logger.info(
            "lifecycle transition",
            extra={
                "source": self._source,
                "from": event.from_state.value,
                "to": event.to_state.value,
                "reason": reason,
            },
        )

        for listener in self._listeners:
            try:
                listener(event)
            except Exception:
                logger.exception("lifecycle listener failed")

        return event

    def on_transition(self, callback: Callable[[LifecycleEvent], None]) -> None:
        self._listeners.append(callback)

    def reset(self) -> None:
        """Reset para CREATED (uso em testes)."""
        self._state = LifecycleState.CREATED
        self._history.clear()
