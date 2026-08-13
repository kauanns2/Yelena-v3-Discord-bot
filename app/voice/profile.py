"""Identidade vocal — natural, conversa de call."""

from __future__ import annotations

import os
import random
import re

DEFAULT_VOICE = (os.getenv("YELENA_TTS_VOICE") or "pt-BR-FranciscaNeural").strip()
# mais lento e menos “apresentadora”
DEFAULT_RATE = os.getenv("YELENA_TTS_RATE", "-12%")
DEFAULT_PITCH = os.getenv("YELENA_TTS_PITCH", "+1Hz")
DEFAULT_VOLUME = os.getenv("YELENA_TTS_VOLUME", "-2%")

VOICE_BRIEF = (
    "Voz feminina jovem (~22), natural de call. Sem narradora, sem assistente."
)


def prepare_spoken_text(text: str, *, emotion: str | None = None) -> str:
    t = (text or "").strip()
    if not t:
        return t

    t = re.sub(r"[*_`#>]+", "", t)
    t = re.sub(r"\s*\n\s*", ". ", t)
    t = re.sub(r"\s{2,}", " ", t).strip()
    t = re.sub(r"!{2,}", "!", t)

    # remove tom de sistema / tutorial
    for bad in (
        "Entrei na call",
        "tô te ouvindo",
        "Fala no microfone",
        "transformo em texto",
        "OPENAI",
        "API",
    ):
        if bad.lower() in t.lower() and len(t) < 120:
            # se a resposta inteira é meta, troca
            if t.lower().startswith("entrei") or "microfone" in t.lower():
                return random.choice(["Oi.", "Pode falar.", "Tô aqui."])

    # respostas curtas soam menos robóticas no TTS
    if len(t) > 140:
        t = t[:137].rsplit(" ", 1)[0] + "..."

    if len(t) > 20 and random.random() < 0.08:
        t = random.choice(["Hm... ", "É... ", ""]) + t

    if emotion in {"serious", "concern", "sad"}:
        t = t.replace("!", ".")

    return t.strip()
