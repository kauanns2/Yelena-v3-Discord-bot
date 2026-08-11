"""Detecção simples de intenções conversacionais."""

from __future__ import annotations

import re

from app.conversation.constants import IntentType
from app.conversation.models.turn import Intent


GREETING_PATTERNS = re.compile(r"\b(oi|olá|ola|hey|eai|e aí|bom dia|boa tarde|boa noite|hello|hi)\b", re.I)
FAREWELL_PATTERNS = re.compile(r"\b(tchau|até|ate logo|flw|bye|adeus|até mais)\b", re.I)
QUESTION_PATTERNS = re.compile(r"\?|\b(o que|oque|qual|quais|como|por que|porque|quando|onde|quem)\b", re.I)
CONFIRM_PATTERNS = re.compile(r"\b(sim|yes|confirmo|pode|ok|okay|certo|isso)\b", re.I)
DENY_PATTERNS = re.compile(r"\b(não|nao|no|nunca|jamais|nega)\b", re.I)
ACTION_PATTERNS = re.compile(r"\b(execute|faça|faz|delete|apague|rode|implemente|crie|modifique)\b", re.I)


def detect_intent(text: str) -> Intent:
    text = text.strip()
    if not text:
        return Intent(intent_type=IntentType.UNKNOWN, confidence=0.2, raw=text)

    if GREETING_PATTERNS.search(text) and len(text) < 40:
        return Intent(intent_type=IntentType.GREETING, confidence=0.9, raw=text)

    if FAREWELL_PATTERNS.search(text) and len(text) < 40:
        return Intent(intent_type=IntentType.FAREWELL, confidence=0.85, raw=text)

    if ACTION_PATTERNS.search(text):
        return Intent(intent_type=IntentType.ACTION, confidence=0.75, raw=text)

    if QUESTION_PATTERNS.search(text):
        return Intent(intent_type=IntentType.QUESTION, confidence=0.7, raw=text)

    if CONFIRM_PATTERNS.search(text) and len(text) < 30:
        return Intent(intent_type=IntentType.CONFIRMATION, confidence=0.7, raw=text)

    if DENY_PATTERNS.search(text) and len(text) < 30:
        return Intent(intent_type=IntentType.DENIAL, confidence=0.7, raw=text)

    if len(text) < 20:
        return Intent(intent_type=IntentType.STATEMENT, confidence=0.5, raw=text)

    return Intent(intent_type=IntentType.STATEMENT, confidence=0.55, raw=text)
