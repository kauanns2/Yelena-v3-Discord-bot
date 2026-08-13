"""Identidade vocal da Yelena.

Direção:
- Clareza e juventude (referência estética de voz jovem limpa),
  mas **sem** tom de anime / personagem sintetizada.
- Puxar para realismo de garota ~20–23 em call de Discord.
- Não é clone de nenhuma personagem comercial; é um perfil próprio.
"""

from __future__ import annotations

import os
import random
import re

DEFAULT_VOICE = (os.getenv("YELENA_TTS_VOICE") or "pt-BR-FranciscaNeural").strip()
# rate quase natural; pitch um pouco acima = mais jovem, sem gritar anime
DEFAULT_RATE = os.getenv("YELENA_TTS_RATE", "+2%")
DEFAULT_PITCH = os.getenv("YELENA_TTS_PITCH", "+5Hz")
DEFAULT_VOLUME = os.getenv("YELENA_TTS_VOLUME", "+0%")

VOICE_BRIEF = (
    "Voz feminina jovem (~22), clara e natural, como em call de Discord. "
    "Sem narração, sem anime, sem assistente. Português brasileiro; "
    "sotaque russo só quando o clone/futuro provider permitir."
)

# suaviza padrões que soam "personagem"
_ANIME_TRIM = [
    (re.compile(r"!{2,}"), "!"),
    (re.compile(r"\?{2,}"), "?"),
    (re.compile(r"~+"), ""),
    (re.compile(r"\bnya+\b", re.I), ""),
    (re.compile(r"\bdesu\b", re.I), ""),
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

    # hesitação humana rara — não “cute”
    if len(t) > 16 and random.random() < 0.12:
        t = random.choice(["Hm... ", "É... ", ""]) + t

    if emotion in {"serious", "concern", "sad"}:
        t = t.replace("!", ".")

    if len(t) > 320:
        t = t[:317].rstrip() + "..."
    return t.strip()
