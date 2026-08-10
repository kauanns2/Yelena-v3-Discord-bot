"""Testes do LifecycleManager."""

import pytest

from app.core.constants import LifecycleState
from app.core.exceptions import LifecycleError
from app.core.lifecycle import LifecycleManager


def test_initial_state():
    lm = LifecycleManager()
    assert lm.state == LifecycleState.CREATED


def test_valid_transition():
    lm = LifecycleManager()
    lm.transition(LifecycleState.BOOTSTRAPPING, reason="test")
    assert lm.state == LifecycleState.BOOTSTRAPPING
    lm.transition(LifecycleState.STARTING)
    assert lm.state == LifecycleState.STARTING
    lm.transition(LifecycleState.RUNNING)
    assert lm.state == LifecycleState.RUNNING


def test_invalid_transition():
    lm = LifecycleManager()
    with pytest.raises(LifecycleError):
        lm.transition(LifecycleState.RUNNING)


def test_history():
    lm = LifecycleManager()
    lm.transition(LifecycleState.BOOTSTRAPPING)
    lm.transition(LifecycleState.STARTING)
    assert len(lm.history) == 2
    assert lm.history[0].to_state == LifecycleState.BOOTSTRAPPING
