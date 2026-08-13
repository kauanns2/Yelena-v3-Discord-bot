"""Camada leve de fala — PT-BR normal, sotaque russo opcional e sutil."""

from __future__ import annotations

import random
import re

SPEECH_STYLE_HINT = (
    "Fala português brasileiro claro e objetivo. "
    "Sotaque russo leve (R um pouco mais marcado só de vez em quando). "
    "Não peça contexto genérico; responda com o que tem e complete o raciocínio. "
    "Sem tom de assistente corporativo. Sem desculpa de IA a cada frase. "
    "Pode discordar e dar opinião direta."
)

_R_FOCUS = re.compile(
    r"\b(claro|certo|melhor|problema|importante|respeito|errado|"
    r"lembrar|primeiro|criar|russa|Rússia|Brasil)\b",
    re.I,
)


def color_speech(text: str, *, intensity: float = 0.2) -> str:
    """Quase neutro: no máximo um toque de R russo."""
    if not text or not text.strip():
        return text
    out = text.strip()
    if random.random() < 0.12 * max(intensity, 0.15):
        out = _russian_r_touch(out)
    return re.sub(r"\s{2,}", " ", out).strip()


def _russian_r_touch(text: str) -> str:
    matches = list(_R_FOCUS.finditer(text))
    if not matches:
        return text
    m = random.choice(matches)
    start, end = m.span()
    word = text[start:end]

    def repl(mm: re.Match[str]) -> str:
        g = mm.group(0)
        if len(g) >= 2:
            return g
        return g + ("r" if random.random() < 0.4 else "")

    return text[:start] + re.sub(r"r+", repl, word, count=1, flags=re.I) + text[end:]
