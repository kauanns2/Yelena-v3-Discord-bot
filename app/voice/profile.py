"""Perfil vocal da Yelena — alvo de produção.

Descrição canônica (para TTS atual e clone futuro):
- Feminina, ~20–23 anos, russa falando pt-BR
- Natural de call Discord (não narradora / não assistente)
- Sotaque russo leve; R um pouco mais marcado às vezes
- Ritmo variável, pausas, hesitações discretas
"""

from __future__ import annotations

import os
import random
import re

# edge-tts: melhor aproximação gratuita disponível em pt-BR jovem
DEFAULT_VOICE = os.getenv("YELENA_TTS_VOICE", "pt-BR-FranciscaNeural").strip()
# Thalita multilingual costuma soar um pouco mais natural em alguns trechos
ALT_VOICE = "pt-BR-ThalitaMultilingualNeural"

# Ajustes para soar mais jovem / leve (sem caricatura)
DEFAULT_RATE = os.getenv("YELENA_TTS_RATE", "+6%")
DEFAULT_PITCH = os.getenv("YELENA_TTS_PITCH", "+3Hz")
DEFAULT_VOLUME = os.getenv("YELENA_TTS_VOLUME", "+0%")

VOICE_BRIEF = (
    "Garota russa ~22 anos em call de Discord. Português brasileiro fluente, "
    "sotaque russo leve e natural. Voz delicada, pitch médio-alto, conversacional, "
    "não narradora, não assistente, não anime."
)


def prepare_spoken_text(text: str, *, emotion: str | None = None) -> str:
    """Leve humanização do texto antes do TTS (sem exagero)."""
    t = (text or "").strip()
    if not t:
        return t

    # remove markdown / listas que soam robóticas em voz
    t = re.sub(r"[*_`#>]+", "", t)
    t = re.sub(r"\s*\n\s*", ". ", t)
    t = re.sub(r"\s{2,}", " ", t).strip()

    # hesitação ocasional no começo (conversa real)
    if len(t) > 12 and random.random() < 0.18:
        t = random.choice(["Hm... ", "É... ", "Olha... ", ""]) + t

    # emoção só modula pontuação/ritmo textual (TTS não lê SSML rico no edge)
    if emotion in {"happy", "curiosity", "joy"} and not t.endswith("?"):
        if random.random() < 0.25:
            t = t.rstrip(".") + "."
    if emotion in {"serious", "concern", "sad"}:
        t = t.replace("!", ".")

    # limite de fala por turno na call
    if len(t) > 320:
        t = t[:317].rstrip() + "..."
    return t
