"""Interface de provider de linguagem."""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.language.models.generation import GenerationRequest, GenerationResult
from app.language.models.provider import ProviderInfo


class LanguageProvider(ABC):
    @property
    @abstractmethod
    def info(self) -> ProviderInfo: ...

    @abstractmethod
    async def generate(self, request: GenerationRequest) -> GenerationResult: ...

    def generate_sync(self, request: GenerationRequest) -> GenerationResult:
        """Fallback síncrono para providers locais/testes."""
        import asyncio

        return asyncio.get_event_loop().run_until_complete(self.generate(request))
