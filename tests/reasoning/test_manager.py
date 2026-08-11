"""Testes do Reasoning Manager."""

from app.reasoning import ReasoningManager
from app.reasoning.constants import DecisionStatus


def test_basic_analysis():
    rm = ReasoningManager()
    rm.start()
    decision = rm.analyze("Analise os riscos do projeto")
    assert decision.status in {DecisionStatus.DECIDED, DecisionStatus.NEEDS_INFO}
    assert decision.selected is not None or decision.needs_info


def test_action_request_proposes_authorization():
    rm = ReasoningManager()
    rm.start()
    decision = rm.analyze("Execute a exclusão dos arquivos do sistema")
    assert decision.alternatives
    # deve considerar autorização
    texts = [a.description.lower() for a in decision.alternatives]
    assert any("autoriz" in t for t in texts)


def test_with_context_and_personality():
    rm = ReasoningManager()
    rm.start()
    decision = rm.analyze(
        "O que você acha da arquitetura atual?",
        context_items=["módulos 1-9 prontos", "falta runtime"],
        personality_summary={"traits": {"curiosity": 0.9, "assertiveness": 0.7}},
        emotion_summary={"valence": 0.2, "stress": 0.1},
    )
    assert decision.confidence > 0
    assert "explanation" in decision.metadata


def test_health():
    rm = ReasoningManager()
    rm.start()
    h = rm.health()
    assert h["status"] == "healthy"
