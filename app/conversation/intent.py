"""Detecção simples de intenções conversacionais."""

from __future__ import annotations

import re

from app.conversation.constants import IntentType
from app.conversation.models.turn import Intent


GREETING_PATTERNS = re.compile(
    r"\b(oi|oie|oiê|olá|ola|hey|eai|eae|e aí|salve|fala|bom dia|boa tarde|boa noite|hello|hi)\b",
    re.I,
)
WELLBEING_PATTERNS = re.compile(
    r"\b(tudo bem|td bem|tudo bom|td bom|como (você|vc|ce|cê) (está|esta|tá|ta)|como vai)\b",
    re.I,
)
FAREWELL_PATTERNS = re.compile(r"\b(tchau|até|ate logo|flw|bye|adeus|até mais)\b", re.I)
QUESTION_PATTERNS = re.compile(
    r"\?|\b(o que|oque|qual|quais|como|por que|porque|quando|onde|quem)\b", re.I
)
CONFIRM_PATTERNS = re.compile(r"\b(sim|yes|confirmo|pode|ok|okay|certo|isso)\b", re.I)
DENY_PATTERNS = re.compile(r"\b(não|nao|no|nunca|jamais|nega)\b", re.I)
ACTION_PATTERNS = re.compile(
    r"\b(execute|faça|faz|delete|apague|rode|implemente|crie|modifique|manda|envie)\b", re.I
)
NAME_STRIP = re.compile(r"\byelena\b", re.I)


def _normalize(text: str) -> str:
    t = text.strip()
    t = NAME_STRIP.sub(" ", t)
    return re.sub(r"\s+", " ", t).strip()


def detect_intent(text: str) -> Intent:
    raw = text.strip()
    if not raw:
        return Intent(intent_type=IntentType.UNKNOWN, confidence=0.2, raw=raw)

    cleaned = _normalize(raw)

    if WELLBEING_PATTERNS.search(cleaned) or WELLBEING_PATTERNS.search(raw):
        return Intent(intent_type=IntentType.QUESTION, confidence=0.88, raw=raw)

    if GREETING_PATTERNS.search(cleaned) and len(cleaned) < 48:
        return Intent(intent_type=IntentType.GREETING, confidence=0.9, raw=raw)

    if FAREWELL_PATTERNS.search(cleaned) and len(cleaned) < 40:
        return Intent(intent_type=IntentType.FAREWELL, confidence=0.85, raw=raw)

    if ACTION_PATTERNS.search(cleaned):
        return Intent(intent_type=IntentType.ACTION, confidence=0.75, raw=raw)

    if QUESTION_PATTERNS.search(cleaned):
        return Intent(intent_type=IntentType.QUESTION, confidence=0.7, raw=raw)

    if CONFIRM_PATTERNS.search(cleaned) and len(cleaned) < 30:
        return Intent(intent_type=IntentType.CONFIRMATION, confidence=0.7, raw=raw)

    if DENY_PATTERNS.search(cleaned) and len(cleaned) < 30:
        return Intent(intent_type=IntentType.DENIAL, confidence=0.7, raw=raw)

    if len(cleaned) < 20:
        return Intent(intent_type=IntentType.STATEMENT, confidence=0.5, raw=raw)

    return Intent(intent_type=IntentType.STATEMENT, confidence=0.55, raw=raw)
