"""Contrato de provider TTS — edge hoje, clone amanhã."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path


class TTSProvider(ABC):
    @property
    @abstractmethod
    def id(self) -> str: ...

    @abstractmethod
    async def synthesize(self, text: str) -> Path | None:
        """Gera arquivo de áudio temporário."""
