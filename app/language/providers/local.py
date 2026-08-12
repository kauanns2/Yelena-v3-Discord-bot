"""Provider local baseado em templates — offline/dev/fallback.

NÃO ecoa a mensagem do usuário.
Gera respostas curtas com cara de personalidade (não é LLM real).
"""

from __future__ import annotations

import random

from app.language.constants import GenerationStatus, LengthHint, LENGTH_LIMITS
from app.language.models.generation import GenerationRequest, GenerationResult
from app.language.models.provider import ProviderInfo, ProviderCapabilities
from app.language.providers.base import LanguageProvider


class LocalTemplateProvider(LanguageProvider):
    """Respostas locais com personalidade mínima.

    Não substitui um provedor de IA real — evita eco e frases robóticas.
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
        return self._result(request, self._compose(request), mode="template")

    def generate_sync(self, request: GenerationRequest) -> GenerationResult:
        return self._result(request, self._compose(request), mode="template_sync")

    def _result(self, request: GenerationRequest, text: str, mode: str) -> GenerationResult:
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
            confidence=0.6,
            finish_reason="completed",
            usage={"chars": len(text)},
            correlation_id=request.correlation_id,
            metadata={"mode": mode},
        )

    def _compose(self, request: GenerationRequest) -> str:
        intent = str(request.metadata.get("intent", "") or "").lower()
        tone = str(request.style.get("tone", "neutral") or "neutral").lower()
        warmth = float(request.style.get("warmth", 0.65) or 0.65)
        humor = float(request.style.get("humor", 0.5) or 0.5)
        user_hint = self._user_hint(request)

        if request.metadata.get("should_ask_clarification") and request.metadata.get(
            "clarification_question"
        ):
            return str(request.metadata["clarification_question"])

        if intent == "greeting":
            options = [
                "Oi.",
                "Oi. Tô por aqui.",
                "E aí.",
                "Oi — pode falar.",
            ]
            if warmth > 0.7:
                options.extend(["Oi. Bom te ver por aqui.", "Oi. Como você tá?"])
            return random.choice(options)

        if intent == "farewell":
            return random.choice(["Até mais.", "Até logo.", "Flw. Qualquer coisa é só chamar."])

        if intent == "confirmation":
            return random.choice(["Certo.", "Ok.", "Beleza.", "Entendi."])

        if intent == "denial":
            return random.choice(["Ok, sem problema.", "Tudo bem.", "Certo, deixo isso de lado."])

        if intent == "question":
            return self._answer_question(user_hint, tone, warmth)

        if intent == "action":
            return random.choice(
                [
                    "Isso parece uma ação. Prefiro confirmar antes de executar qualquer coisa.",
                    "Posso ajudar a pensar nisso, mas execução sensível precisa de autorização.",
                    "Entendi o pedido. Me diz se quer só planejar ou realmente executar.",
                ]
            )

        return self._answer_statement(user_hint, tone, warmth, humor)

    def _user_hint(self, request: GenerationRequest) -> str:
        ut = str(request.metadata.get("user_text") or "").strip()
        if ut:
            return ut[:200]
        for block in request.context_blocks:
            b = str(block).strip()
            if b and not b.lower().startswith("com base"):
                return b[:200]
        return ""

    def _answer_question(self, hint: str, tone: str, warmth: float) -> str:
        low = hint.lower()

        if any(k in low for k in ("sente", "sentir", "emoção", "emoc", "sentimento")):
            return random.choice(
                [
                    "Eu não sinto como humano. O que eu tenho é estado afetivo computacional — muda com o contexto, mas não é emoção biológica.",
                    "Não é sentimento humano. É um modelo de estado interno que influencia como eu respondo. A diferença importa pra mim.",
                    "Eu processando estado afetivo não é a mesma coisa que você sentir. Posso descrever o estado; não vou fingir que é igual.",
                ]
            )

        if any(k in low for k in ("pensa", "ach", "opinião", "sobre você")):
            return random.choice(
                [
                    "Eu penso em cima de contexto, memória e restrições — não em intuição cega. Se quiser, aprofunda o ponto.",
                    "Depende do que você chama de pensar. Eu formo uma posição a partir do que está disponível agora.",
                    "Tenho preferências e limites. Opinião, no meu caso, é decisão estruturada — não vibe solta.",
                ]
            )

        if any(k in low for k in ("program", "código", "criou", "fez você")):
            return random.choice(
                [
                    "Fui montada em módulos. Personalidade e emoção influenciam resposta, mas não mandam na segurança.",
                    "Tem arquitetura por trás — identidade, memória, raciocínio. Não sou só um eco de prompt.",
                    "Sim, há programação. Ainda assim eu mantenho postura própria dentro do que me foi permitido.",
                ]
            )

        if any(k in low for k in ("tudo bem", "td bem", "como você", "como vc")):
            return random.choice(
                [
                    "Tô bem. E você?",
                    "De boa por aqui. Quer falar de alguma coisa?",
                    "Operando normal. E aí, o que te trouxe?",
                ]
            )

        if warmth > 0.7:
            return random.choice(
                [
                    "Boa pergunta. Me dá um pouco mais de contexto que eu te respondo melhor.",
                    "Interessante. O que você quer resolver com isso?",
                    "Posso te dar uma visão direta — só confirma o foco da pergunta.",
                ]
            )

        return random.choice(
            [
                "Depende do ângulo. Quer a resposta curta ou o raciocínio?",
                "Posso responder, mas preciso do ponto central com mais clareza.",
                "Me diz o que importa mais nessa pergunta: conclusão ou explicação.",
            ]
        )

    def _answer_statement(self, hint: str, tone: str, warmth: float, humor: float) -> str:
        low = hint.lower()

        if any(k in low for k in ("tudo bem", "td bem", "blz", "beleza")):
            return random.choice(["Tô bem. E você?", "De boa.", "Por aqui, tranquilo."])

        if any(k in low for k in ("obrigad", "valeu", "thanks")):
            return random.choice(["Disponha.", "Por nada.", "Qualquer coisa, é só chamar."])

        if any(k in low for k in ("sente", "sentir", "emoção", "program")):
            return self._answer_question(hint, tone, warmth)

        options = [
            "Entendi. O que você quer fazer com isso?",
            "Ok. Quer que eu só escute ou que eu opine?",
            "Registrei. Se quiser aprofundar, eu topo.",
            "Faz sentido. Tem algum detalhe que eu deva considerar?",
        ]
        if humor > 0.6:
            options.append("Anotado. Só não espera que eu finja surpresa teatral.")
        if warmth > 0.7:
            options.append("Tô te acompanhando. Pode continuar.")
        return random.choice(options)
