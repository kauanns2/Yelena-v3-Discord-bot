"""Testes de propagação."""

import pytest

from app.neural.manager import NeuralWebManager
from app.neural.models.signal import Signal
from app.neural.constants import NodeType, SignalType
from app.neural.errors import TTLExpiredError, LoopDetectedError


def test_direct_delivery():
    web = NeuralWebManager()
    web.register_node("a", NodeType.MODULE)
    web.register_node("b", NodeType.MODULE)
    web.connect("a", "b")

    received = []
    web.on_signal("b", lambda sig, nid: received.append(sig.payload))

    signal = Signal(
        signal_type=SignalType.EVENT,
        source_id="a",
        target_id="b",
        payload={"msg": "hello"},
    )
    delivered = web.emit(signal)
    assert "b" in delivered
    assert received == [{"msg": "hello"}]


def test_ttl_expired():
    web = NeuralWebManager()
    web.register_node("a", NodeType.MODULE)
    web.register_node("b", NodeType.MODULE)

    signal = Signal(
        signal_type=SignalType.EVENT,
        source_id="a",
        target_id="b",
        ttl=0.0,
    )
    # force expired
    signal.created_at = 0.0
    with pytest.raises(TTLExpiredError):
        web.emit(signal)


def test_loop_blocked():
    web = NeuralWebManager()
    web.register_node("a", NodeType.MODULE)
    web.register_node("b", NodeType.MODULE)

    signal = Signal(
        signal_type=SignalType.EVENT,
        source_id="a",
        target_id="b",
        path=["b"],  # already visited
    )
    with pytest.raises(LoopDetectedError):
        web.emit(signal)
