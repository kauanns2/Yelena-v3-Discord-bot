"""Language Manager."""

from __future__ import annotations

import logging
from typing import Any

from app.language.builder import InstructionBuilder
from app.language.constants import GenerationStatus
from app.language.errors import GenerationError, ProviderError
from app.language.models.generation import GenerationRequest, GenerationResult
from app.language.postprocess import postprocess
from app.language.providers.local import LocalTemplateProvider
from app.language.providers.llm_chat import LLMChatProvider, llm_configured
from app.language.providers.registry import ProviderRegistry

logger = logging.getLogger(__name__)


class LanguageManager:
    def __init__(self) -> None:
        self._registry = ProviderRegistry()
        self._builder = InstructionBuilder()
        self._started = False
        self._metrics = {"generations": 0, "fallbacks": 0, "failures": 0}
        self._registry.register(LocalTemplateProvider())
        if llm_configured():
            self._registry.register(LLMChatProvider())
            logger.info("LLM chat provider registered (priority high)")
        else:
            logger.warning(
                "LLM NÃO configurado — só template local. "
                "Defina GROQ_API_KEY ou OPENAI_API_KEY no Render."
            )

    @property
    def is_started(self) -> bool:
        return self._started

    def start(self) -> None:
        self._started = True
        logger.info("language system started providers=%s", self._registry.list_providers())

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
            logger.info(
                "language used provider=%s mode=%s",
                result.provider_id,
                (result.metadata or {}).get("mode"),
            )
            return result
        except Exception as primary_exc:
            logger.error("primary provider failed (%s): %s", getattr(provider.info, "id", "?"), primary_exc)
            self._metrics["failures"] += 1
            try:
                fallback = self._registry.require("local_template")
                result = fallback.generate_sync(request)
                result.status = GenerationStatus.FALLBACK
                result.metadata["fallback_from"] = getattr(provider.info, "id", "unknown")
                result.metadata["fallback_error"] = str(primary_exc)[:200]
                result = postprocess(result, request.length)
                self._metrics["fallbacks"] += 1
                logger.warning("language FALLBACK to local_template")
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
            "llm_configured": llm_configured(),
            "metrics": dict(self._metrics),
        }
