"""Correção leve de texto vindo do STT."""

from __future__ import annotations

import re

# trocas comuns de reconhecimento em pt-BR
_REPLACEMENTS = [
    (re.compile(r"\byelena\b", re.I), "Yelena"),
    (re.compile(r"\byelenaa\b", re.I), "Yelena"),
    (re.compile(r"\bcaua\b", re.I), "Kauã"),
    (re.compile(r"\bkaua\b", re.I), "Kauã"),
    (re.compile(r"\bvc\b", re.I), "você"),
    (re.compile(r"\btb\b", re.I), "também"),
    (re.compile(r"\bpq\b", re.I), "porque"),
    (re.compile(r"\btd\b", re.I), "tudo"),
]

_FILLER = re.compile(r"\b(uh+|uhm+|ã+h+|ééé+)\b", re.I)
_SPACES = re.compile(r"\s{2,}")


def correct_transcript(text: str) -> str:
    t = (text or "").strip()
    if not t:
        return t
    t = _FILLER.sub("", t)
    for pat, rep in _REPLACEMENTS:
        t = pat.sub(rep, t)
    t = _SPACES.sub(" ", t).strip()
    # capitaliza início
    if t and t[0].islower():
        t = t[0].upper() + t[1:]
    return t
