"""Testes do Bridge Manager."""

from app.bridge import BridgeManager
from app.bridge.constants import ContinuityNamespace
from app.bridge.platforms.base import InboundMessage
from app.runtime import YelenaRuntime


def test_continuity_put_get():
    bm = BridgeManager()
    bm.start()
    bm.deposit(ContinuityNamespace.SYSTEM, "hello", {"x": 1})
    assert bm.recall(ContinuityNamespace.SYSTEM, "hello") == {"x": 1}
    bm.stop()


def test_handle_inbound_with_runtime():
    rt = YelenaRuntime()
    rt.start()
    bm = BridgeManager(process_fn=rt.process)
    bm.start()

    inbound = InboundMessage(
        text="oi",
        user_id="1",
        channel_id="c1",
        platform="test",
    )
    out = bm.handle_inbound(inbound)
    assert out.text
    bm.stop()
    rt.stop()


def test_evolution_record():
    bm = BridgeManager()
    bm.start()
    ev = bm.evolution.record("test", "unit test event", source_module="tests")
    assert ev.id
    recent = bm.evolution.recent(5)
    assert any(e.get("id") == ev.id for e in recent)
    bm.stop()
