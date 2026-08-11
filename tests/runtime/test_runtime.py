"""Testes do Runtime."""

from app.runtime import YelenaRuntime
from app.runtime.constants import RuntimeState, Complexity
from app.runtime.classifier import classify_complexity


def test_classify_trivial():
    assert classify_complexity("oi") == Complexity.TRIVIAL
    assert classify_complexity("tchau") == Complexity.TRIVIAL


def test_classify_critical():
    assert classify_complexity("execute a exclusão agora") == Complexity.CRITICAL


def test_runtime_start_and_process():
    rt = YelenaRuntime()
    rt.start()
    assert rt.state == RuntimeState.READY

    response = rt.process("oi", user_id="test_user")
    assert response.text
    assert "language" in response.modules_used or "conversation" in response.modules_used
    assert response.complexity == Complexity.TRIVIAL

    rt.stop()
    assert rt.state == RuntimeState.STOPPED


def test_runtime_normal_message():
    rt = YelenaRuntime()
    rt.start()
    response = rt.process(
        "O que você acha da arquitetura modular do projeto?",
        user_id="test_user",
    )
    assert response.text
    assert response.complexity in {Complexity.NORMAL, Complexity.COMPLEX, Complexity.SIMPLE}
    rt.stop()


def test_health():
    rt = YelenaRuntime()
    rt.start()
    h = rt.health()
    assert h["state"] == "ready"
    rt.stop()
