"""Registry de providers de linguagem."""

from __future__ import annotations

import logging

from app.language.errors import ProviderError
from app.language.providers.base import LanguageProvider
from app.language.types import ProviderId

logger = logging.getLogger(__name__)


class ProviderRegistry:
    def __init__(self) -> None:
        self._providers: dict[ProviderId, LanguageProvider] = {}

    def register(self, provider: LanguageProvider) -> None:
        pid = provider.info.id
        self._providers[pid] = provider
        logger.info("language provider registered", extra={"provider_id": pid})

    def get(self, provider_id: ProviderId) -> LanguageProvider | None:
        return self._providers.get(provider_id)

    def require(self, provider_id: ProviderId) -> LanguageProvider:
        provider = self.get(provider_id)
        if provider is None:
            raise ProviderError(f"Provider not found: {provider_id}")
        return provider

    def select_default(self) -> LanguageProvider:
        enabled = [p for p in self._providers.values() if p.info.enabled]
        if not enabled:
            raise ProviderError("No language providers available")
        enabled.sort(key=lambda p: p.info.priority, reverse=True)
        return enabled[0]

    def list_providers(self) -> list[str]:
        return list(self._providers.keys())
