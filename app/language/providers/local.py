"""Provider local baseado em templates — offline/dev/fallback."""

from __future__ import annotations

from app.language.constants import GenerationStatus, LengthHint, LENGTH_LIMITS
from app.language.models.generation import GenerationRequest, GenerationResult
from app.language.models.provider import ProviderInfo, ProviderCapabilities
from app.language.providers.base import LanguageProvider


class LocalTemplateProvider(LanguageProvider):
    """Gera respostas simples sem API externa.

    Útil para testes, fallback e desenvolvimento.
    """

    def __init__(self) -> None:
        self._info = ProviderInfo(
            id="local_template",
            name="Local Template Provider",
            capabilities=ProviderCapabilities(
                supports_streaming=False,
                supports_system_prompt=False,
                max_tokens=1024,
            ),
            priority=10,
        )

    @property
    def info(self) -> ProviderInfo:
        return self._info

    async def generate(self, request: GenerationRequest) -> GenerationResult:
        text = self._compose(request)
        limit = LENGTH_LIMITS.get(
            request.length if isinstance(request.length, LengthHint) else LengthHint.MEDIUM,
            400,
        )
        if len(text) > limit:
            text = text[: limit - 3].rstrip() + "..."

        return GenerationResult(
            text=text,
            status=GenerationStatus.SUCCESS,
            provider_id=self._info.id,
            request_id=request.id,
            confidence=0.55,
            finish_reason="completed",
            usage={"chars": len(text)},
            correlation_id=request.correlation_id,
            metadata={"mode": "template"},
        )

    def generate_sync(self, request: GenerationRequest) -> GenerationResult:
        import asyncio

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(self.generate(request))
        # se já há loop, compor de forma síncrona direta
        text = self._compose(request)
        limit = LENGTH_LIMITS.get(
            request.length if isinstance(request.length, LengthHint) else LengthHint.MEDIUM,
            400,
        )
        if len(text) > limit:
            text = text[: limit - 3].rstrip() + "..."
        return GenerationResult(
            text=text,
            status=GenerationStatus.SUCCESS,
            provider_id=self._info.id,
            request_id=request.id,
            confidence=0.55,
            correlation_id=request.correlation_id,
            metadata={"mode": "template_sync"},
        )

    def _compose(self, request: GenerationRequest) -> str:
        parts: list[str] = []
        intent = request.metadata.get("intent", "")
        tone = request.style.get("tone", "neutral")

        if intent == "greeting":
            if request.context_blocks:
                parts.append("Oi. Ainda pensando naquilo?")
            elif tone == "warm":
                parts.append("Oi ❤️")
            else:
                parts.append("Oi.")
            return parts[0]

        if intent == "farewell":
            return "Até mais."

        if request.metadata.get("should_ask_clarification") and request.metadata.get("clarification_question"):
            return str(request.metadata["clarification_question"])

        if request.key_points:
            # montagem simples a partir dos pontos
            body = []
            for point in request.key_points[:4]:
                if point.startswith("responder") or point.startswith("usar"):
                    continue
                body.append(f"• {point}")
            if request.context_blocks:
                body.append("Com base no que sei: " + request.context_blocks[0][:120])
            if not body:
                body.append("Entendi. Vou considerar o contexto e te responder com cuidado.")
            return "\n".join(body)

        if request.instructions:
            return request.instructions[:300]

        return "Entendi. Pode me dar mais detalhes?"
