"""Detecta pedido de áudio/voz."""

from __future__ import annotations

import os
import random
import re

AUDIO_REQUEST_RE = re.compile(
    r"\b(áudio|audio|voz|voice|manda (um )?áudio|envie (um )?áudio|"
    r"responde em áudio|fala em áudio|manda voz|em áudio)\b",
    re.I,
)


def wants_audio(text: str, *, auto_rate: float | None = None) -> bool:
    if AUDIO_REQUEST_RE.search(text or ""):
        return True
    try:
        rate = float(os.getenv("YELENA_VOICE_AUTO", "0") or "0") if auto_rate is None else auto_rate
    except ValueError:
        rate = 0.0
    rate = max(0.0, min(1.0, float(rate)))
    return rate > 0 and random.random() < rate
