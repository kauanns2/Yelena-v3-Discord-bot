"""Testes do Conversation Manager."""

import pytest

from app.conversation import ConversationManager
from app.conversation.constants import IntentType, SessionStatus
from app.conversation.errors import SessionNotFoundError


def test_create_and_process_greeting():
    cm = ConversationManager()
    cm.start()
    session = cm.create_session(user_id="u1")
    turn, spec = cm.process_message(session.id, "oi")
    assert turn.intent is not None
    assert turn.intent.intent_type == IntentType.GREETING
    assert spec.max_length == "short"


def test_question_may_clarify():
    cm = ConversationManager()
    cm.start()
    session = cm.create_session()
    turn, spec = cm.process_message(session.id, "o que você acha?")
    assert turn.intent.intent_type == IntentType.QUESTION


def test_action_intent():
    cm = ConversationManager()
    cm.start()
    session = cm.create_session()
    turn, spec = cm.process_message(session.id, "execute a limpeza dos arquivos")
    assert turn.intent.intent_type == IntentType.ACTION
    assert any("autoriz" in k.lower() for k in spec.key_points)


def test_session_not_found():
    cm = ConversationManager()
    cm.start()
    with pytest.raises(SessionNotFoundError):
        cm.process_message("missing", "oi")


def test_context_residue_on_greeting():
    cm = ConversationManager()
    cm.start()
    session = cm.create_session()
    _, spec = cm.process_message(
        session.id,
        "oi",
        context_summary=["usuário preocupado com o projeto"],
    )
    assert any("contexto" in k.lower() for k in spec.key_points)
