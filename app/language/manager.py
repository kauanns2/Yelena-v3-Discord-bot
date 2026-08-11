"""Language Manager."""

from __future__ import annotations

import logging
from typing import Any

from app.language.builder import InstructionBuilder
from app.language.constants import GenerationStatus
from app.language.errors import ProviderError, GenerationError
from app.language.models.generation import GenerationRequest, GenerationResult
from app.language.postprocess import postprocess
from app.language.providers.local import LocalTemplateProvider
from app.language.providers.registry import ProviderRegistry

logger = logging.getLogger(__name__)


class LanguageManager:
    """Transforma ResponseSpecification em texto.

    Provider-agnostic. Inclui fallback local.
    """

    def __init__(self) -> None:
        self._registry = ProviderRegistry()
        self._builder = InstructionBuilder()
        self._started = False
        self._metrics = {
            "generations": 0,
            "fallbacks": 0,
            "failures": 0,
        }
        # provider local sempre disponível
        self._registry.register(LocalTemplateProvider())

    @property
    def is_started(self) -> bool:
        return self._started

    def start(self) -> None:
        self._started = True
        logger.info(
            "language system started",
            extra={"providers": self._registry.list_providers()},
        )

    def stop(self) -> None:
        self._started = False

    def register_provider(self, provider: Any) -> None:
        self._registry.register(provider)

    def generate_from_spec(self, spec: Any, provider_id: str | None = None) -> GenerationResult:
        request = self._builder.from_spec(spec)
        return self.generate(request, provider_id=provider_id)

    def generate(self, request: GenerationRequest, provider_id: str | None = None) -> GenerationResult:
        try:
            provider = (
                self._registry.require(provider_id)
                if provider_id
                else self._registry.select_default()
            )
        except ProviderError:
            provider = self._registry.require("local_template")

        try:
            if hasattr(provider, "generate_sync"):
                result = provider.generate_sync(request)
            else:
                import asyncio

                result = asyncio.get_event_loop().run_until_complete(provider.generate(request))
            result = postprocess(result, request.length)
            self._metrics["generations"] += 1
            return result
        except Exception as primary_exc:
            logger.exception("primary provider failed", extra={"error": str(primary_exc)})
            self._metrics["failures"] += 1
            # fallback
            try:
                fallback = self._registry.require("local_template")
                result = fallback.generate_sync(request)
                result.status = GenerationStatus.FALLBACK
                result.metadata["fallback_from"] = getattr(provider.info, "id", "unknown")
                result = postprocess(result, request.length)
                self._metrics["fallbacks"] += 1
                return result
            except Exception as fb_exc:
                self._metrics["failures"] += 1
                raise GenerationError(
                    f"Generation failed: {fb_exc}",
                    context={"primary": str(primary_exc)},
                ) from fb_exc

    def health(self) -> dict[str, Any]:
        return {
            "status": "healthy" if self._started else "stopped",
            "providers": self._registry.list_providers(),
            "metrics": dict(self._metrics),
        }
