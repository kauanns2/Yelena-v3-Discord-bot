"""Identidade vocal da Yelena — mais natural, menos robótica."""

from __future__ import annotations

import os
import random
import re

DEFAULT_VOICE = (os.getenv("YELENA_TTS_VOICE") or "pt-BR-FranciscaNeural").strip()
# mais perto de fala humana (menos "apresentadora")
DEFAULT_RATE = os.getenv("YELENA_TTS_RATE", "-5%")
DEFAULT_PITCH = os.getenv("YELENA_TTS_PITCH", "+2Hz")
DEFAULT_VOLUME = os.getenv("YELENA_TTS_VOLUME", "+0%")

VOICE_BRIEF = (
    "Voz feminina jovem (~22), clara e natural, como em call de Discord. "
    "Sem narração, sem anime, sem assistente."
)

_ANIME_TRIM = [
    (re.compile(r"!{2,}"), "!"),
    (re.compile(r"\?{2,}"), "?"),
    (re.compile(r"~+"), ""),
]


def prepare_spoken_text(text: str, *, emotion: str | None = None) -> str:
    t = (text or "").strip()
    if not t:
        return t

    t = re.sub(r"[*_`#>]+", "", t)
    t = re.sub(r"\s*\n\s*", ". ", t)
    t = re.sub(r"\s{2,}", " ", t).strip()

    for pat, rep in _ANIME_TRIM:
        t = pat.sub(rep, t)

    # frases longas demais soam robóticas no TTS — quebra leve
    if len(t) > 180:
        t = t[:177].rsplit(" ", 1)[0] + "..."

    if len(t) > 14 and random.random() < 0.1:
        t = random.choice(["Hm... ", "É... ", ""]) + t

    if emotion in {"serious", "concern", "sad"}:
        t = t.replace("!", ".")

    return t.strip()
