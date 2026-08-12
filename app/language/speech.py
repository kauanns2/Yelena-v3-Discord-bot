"""SUTAC / coloração de fala da Yelena.

Paulista informal + leve sotaque (r um pouco mais marcado, como influência russa),
sem virar caricatura. Erros leves e hesitações são permitidos.
"""

from __future__ import annotations

import random
import re


def color_speech(text: str, *, intensity: float = 0.35) -> str:
    """Aplica naturalidade leve no texto final."""
    if not text or not text.strip():
        return text

    out = text.strip()

    # ocasionalmente começa com hesitação
    if random.random() < 0.18 * intensity * 2:
        out = random.choice(["hm... ", "ah, ", "olha... ", "sei lá, ", "tipo... "]) + out[0].lower() + out[1:]

    # contrações comuns se ainda estiver formal demais
    replacements = [
        (r"\bvocê está\b", "cê tá"),
        (r"\bVocê está\b", "Cê tá"),
        (r"\bestou\b", "tô"),
        (r"\bEstou\b", "Tô"),
        (r"\bpara o\b", "pro"),
        (r"\bpara a\b", "pra"),
        (r"\bpara\b", "pra"),
        (r"\bvocê\b", "cê"),
        (r"\bVocê\b", "Cê"),
    ]
    if random.random() < 0.55:
        for pat, rep in replacements:
            out = re.sub(pat, rep, out, count=1)

    # leve "r" mais marcado (influência russa) em poucas palavras — não em tudo
    if random.random() < 0.25 * intensity * 2:
        out = _soft_russian_r(out)

    # às vezes deixa frase menos "perfeita" (reticências / corte)
    if random.random() < 0.12 and not out.endswith("?"):
        out = out.rstrip(".") + random.choice(["...", ".", " né?", " sei"])

    return out


def _soft_russian_r(text: str) -> str:
    """Marca o r de forma sutil em 1 palavra (não vira meme)."""
    words = text.split()
    candidates = []
    for i, w in enumerate(words):
        core = re.sub(r"[^\wáéíóúãõâêôàçÁÉÍÓÚÃÕÂÊÔÀÇ]", "", w)
        if len(core) >= 4 and ("r" in core.lower() or "rr" in core.lower()):
            if not core.lower().startswith("http"):
                candidates.append(i)
    if not candidates:
        return text
    i = random.choice(candidates)
    w = words[i]
    # alonga um r interno: melhor -> melhrr / melhórr (leve)
    def _stretch(m: re.Match[str]) -> str:
        return m.group(0) + ("r" if random.random() < 0.5 else "")

    words[i] = re.sub(r"r+", _stretch, w, count=1, flags=re.I)
    return " ".join(words)


SPEECH_STYLE_HINT = (
    "Fala como pessoa real: português brasileiro informal (cara paulista), "
    "contrações (tô, pra, cê), hesitações (hm, tipo, sei lá). "
    "Pode errar português de leve. "
    "Leve sotaque: r um pouco mais puxado (influência russa), sem exagerar. "
    "Nada de tom de assistente corporativo nem desculpa de IA a cada frase."
)
