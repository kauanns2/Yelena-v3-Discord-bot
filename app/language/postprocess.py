"""Pós-processamento e validação de saída."""

from __future__ import annotations

import re

from app.language.constants import LengthHint, LENGTH_LIMITS
from app.language.models.generation import GenerationResult


def normalize_text(text: str) -> str:
    text = text.strip()
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text


def enforce_length(text: str, length: LengthHint | str) -> str:
    try:
        hint = length if isinstance(length, LengthHint) else LengthHint(length)
    except ValueError:
        hint = LengthHint.MEDIUM
    limit = LENGTH_LIMITS[hint]
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def postprocess(result: GenerationResult, length: LengthHint | str = LengthHint.MEDIUM) -> GenerationResult:
    result.text = normalize_text(result.text)
    result.text = enforce_length(result.text, length)
    if not result.text:
        result.text = "..."
        result.confidence = min(result.confidence, 0.3)
    return result
