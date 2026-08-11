"""Testes do Language Manager."""

from app.language import LanguageManager
from app.conversation import ConversationManager
from app.language.constants import GenerationStatus


def test_generate_greeting():
    lm = LanguageManager()
    lm.start()
    cm = ConversationManager()
    cm.start()
    session = cm.create_session()
    _, spec = cm.process_message(session.id, "oi")
    result = lm.generate_from_spec(spec)
    assert result.text
    assert result.status in {GenerationStatus.SUCCESS, GenerationStatus.FALLBACK}


def test_generate_with_context_residue():
    lm = LanguageManager()
    lm.start()
    cm = ConversationManager()
    cm.start()
    session = cm.create_session()
    _, spec = cm.process_message(
        session.id,
        "oi",
        context_summary=["usuário preocupado com o projeto"],
    )
    result = lm.generate_from_spec(spec)
    assert result.text


def test_providers_listed():
    lm = LanguageManager()
    lm.start()
    health = lm.health()
    assert "local_template" in health["providers"]
