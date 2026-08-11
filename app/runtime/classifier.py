"""Classifica complexidade da mensagem para ativação seletiva."""

from __future__ import annotations

import re

from app.runtime.constants import Complexity

GREETING = re.compile(r"^\s*(oi|olá|ola|hey|hi|hello|bom dia|boa tarde|boa noite)\s*[!?.]*\s*$", re.I)
FAREWELL = re.compile(r"^\s*(tchau|flw|bye|até|ate logo|até mais)\s*[!?.]*\s*$", re.I)
ACTION = re.compile(r"\b(execute|faça|delete|apague|rode|implemente|modifique|remova)\b", re.I)


def classify_complexity(message: str) -> Complexity:
    text = message.strip()
    if not text:
        return Complexity.TRIVIAL
    if GREETING.match(text) or FAREWELL.match(text):
        return Complexity.TRIVIAL
    if ACTION.search(text):
        return Complexity.CRITICAL
    if len(text) < 20 and "?" not in text:
        return Complexity.SIMPLE
    if len(text) > 200 or text.count("?") > 1:
        return Complexity.COMPLEX
    return Complexity.NORMAL
