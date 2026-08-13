"""Placeholder para voice clone (ElevenLabs / RVC / etc.).

Quando houver amostra própria da Yelena, implementar aqui
sem mudar o resto do módulo.
"""

from __future__ import annotations

from pathlib import Path

from app.voice.providers.base import TTSProvider


class CloneTTSProvider(TTSProvider):
    """Ainda não ativo — reserva de arquitetura."""

    @property
    def id(self) -> str:
        return "clone_placeholder"

    async def synthesize(self, text: str) -> Path | None:
        return None
