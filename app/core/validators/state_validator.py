"""Validação de transições de estado."""

from __future__ import annotations

from app.core.constants import LifecycleState, VALID_TRANSITIONS
from app.core.exceptions import ValidationError


def validate_transition(from_state: LifecycleState, to_state: LifecycleState) -> None:
    allowed = VALID_TRANSITIONS.get(from_state, set())
    if to_state not in allowed:
        raise ValidationError(
            f"Invalid lifecycle transition: {from_state.value} -> {to_state.value}",
            context={"from": from_state.value, "to": to_state.value},
        )
