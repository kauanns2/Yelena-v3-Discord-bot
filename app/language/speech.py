"""SUTAC da Yelena — fonética paulista + leve R vibrante russo.

Documentação: docs/PHONETICS.md
"""

from __future__ import annotations

import random
import re

# Palavras onde um R mais “presente” soa natural (não força em artigo/pronome)
_R_FOCUS = re.compile(
    r"\b(claro|certo|melhor|pior|verdade|lembrar|lembrar|primeiro|"
    r"problema|importante|respeito|errado|correto|responder|"
    r"procurar|trabalhar|falar|agora|porta|forte|normal|"
    r"histórico|memória|lembrança|criar|criador)\b",
    re.I,
)

SPEECH_STYLE_HINT = (
    "Fala português brasileiro paulista informal: tô, pra, cê, né, tipo, hm. "
    "S em coda alveolar (sem chiado carioca). "
    "R: base brasileira, mas com leve cor russa — R mais presente/vibrado só de vez em quando, "
    "nunca caricatura (sem porrrrta). "
    "Pode hesitar, cortar frase e errar português de leve. "
    "Nada de tom de assistente corporativo nem desculpa de IA a cada mensagem."
)


def color_speech(text: str, *, intensity: float = 0.4) -> str:
    """Aplica naturalidade paulista + toque raro de R russo."""
    if not text or not text.strip():
        return text

    out = text.strip()

    # hesitação inicial ocasional
    if random.random() < 0.22 * max(intensity, 0.2):
        lead = random.choice(["hm... ", "ah, ", "olha... ", "sei lá, ", "tipo... ", "pô, "])
        if out[0].isupper() and len(out) > 1:
            out = lead + out[0].lower() + out[1:]
        else:
            out = lead + out

    # contrações (1–2 por fala)
    out = _apply_contractions(out)

    # R híbrido: no máx. uma palavra marcada
    if random.random() < 0.28 * max(intensity, 0.25):
        out = _russian_r_touch(out)

    # final menos “perfeito”
    if random.random() < 0.14 and not out.endswith(("?", "...", "!")):
        out = out.rstrip(".") + random.choice(["...", " né?", " sei", ""])

    # limpa espaços duplos
    out = re.sub(r"\s{2,}", " ", out).strip()
    return out


def _apply_contractions(text: str) -> str:
    pairs = [
        (r"\bvocê está\b", "cê tá"),
        (r"\bVocê está\b", "Cê tá"),
        (r"\bvocê tá\b", "cê tá"),
        (r"\bVocê tá\b", "Cê tá"),
        (r"\bestou\b", "tô"),
        (r"\bEstou\b", "Tô"),
        (r"\bpara o\b", "pro"),
        (r"\bpara a\b", "pra"),
        (r"\bpara\b", "pra"),
        (r"\bvocê\b", "cê"),
        (r"\bVocê\b", "Cê"),
        (r"\bnão é\b", "né"),
    ]
    # aplica no máximo 2 substituições
    count = 0
    for pat, rep in pairs:
        if count >= 2:
            break
        new, n = re.subn(pat, rep, text, count=1)
        if n:
            text = new
            count += 1
    return text


def _russian_r_touch(text: str) -> str:
    """Marca leve o R em UMA palavra-alvo (vibrante presente, não meme)."""
    matches = list(_R_FOCUS.finditer(text))
    if not matches:
        # fallback: qualquer palavra ≥4 com r
        words = text.split()
        idxs = [
            i
            for i, w in enumerate(words)
            if len(re.sub(r"\W", "", w)) >= 4 and "r" in w.lower()
        ]
        if not idxs:
            return text
        i = random.choice(idxs)
        words[i] = _stretch_r(words[i])
        return " ".join(words)

    m = random.choice(matches)
    start, end = m.span()
    word = text[start:end]
    return text[:start] + _stretch_r(word) + text[end:]


def _stretch_r(word: str) -> str:
    """Alonga no máximo um grupo de r — sinal de vibrante, não 'rrrr'."""

    def repl(m: re.Match[str]) -> str:
        g = m.group(0)
        if len(g) >= 2:
            return g  # já tem rr
        # 50% duplica uma vez só
        return g + ("r" if random.random() < 0.55 else "")

    return re.sub(r"r+", repl, word, count=1, flags=re.I)
