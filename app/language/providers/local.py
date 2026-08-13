"""Provider local — respostas objetivas, sem eco e sem pedir contexto genérico."""

from __future__ import annotations

import random

from app.language.constants import GenerationStatus, LengthHint, LENGTH_LIMITS
from app.language.models.generation import GenerationRequest, GenerationResult
from app.language.models.provider import ProviderInfo, ProviderCapabilities
from app.language.providers.base import LanguageProvider
from app.language.speech import color_speech
from app.world.lore import get_world_summary


class LocalTemplateProvider(LanguageProvider):
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
        text = color_speech(text, intensity=0.25)
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
            confidence=0.65,
            finish_reason="completed",
            usage={"chars": len(text)},
            correlation_id=request.correlation_id,
            metadata={"mode": mode},
        )

    def _compose(self, request: GenerationRequest) -> str:
        intent = str(request.metadata.get("intent", "") or "").lower()
        hint = self._user_hint(request)
        low = hint.lower()

        if request.metadata.get("should_ask_clarification") and request.metadata.get(
            "clarification_question"
        ):
            return str(request.metadata["clarification_question"])

        if intent == "greeting" or low in {"oi", "olá", "ola", "oie", "hey", "hi", "eai"}:
            return random.choice(["Oi.", "Oi. Tô aqui.", "Fala.", "Oi — manda."])

        if intent == "farewell":
            return random.choice(["Até mais.", "Até logo.", "Flw."])

        if intent == "confirmation":
            return random.choice(["Certo.", "Ok.", "Beleza."])

        if intent == "denial":
            return random.choice(["Ok, deixo pra lá.", "Tudo bem.", "Certo."])

        if any(k in low for k in ("áudio", "audio", "voz", "voice", "mandar áudio", "manda um áudio")):
            return random.choice(
                [
                    "Áudio ainda não está ligado no sistema. Por enquanto respondo em texto.",
                    "Não consigo enviar áudio agora — o módulo de voz ainda é reserva. Texto eu mando.",
                    "Permissão de áudio no Discord é uma coisa; gerar voz aqui ainda não está ativo.",
                ]
            )

        if any(k in low for k in ("quantos anos", "idade", "idade você", "tem quantos")):
            return "Vinte e três. Pelo menos é a idade que carrego na história."

        if any(k in low for k in ("russ", "brasil", "de onde", "nasceu", "história", "origem", "sotaque")):
            return get_world_summary()

        if any(k in low for k in ("sente", "sentir", "emoção", "sentimento")):
            return random.choice(
                [
                    "Não é emoção humana. É estado interno que muda prioridade e tom. Eu trato isso com seriedade, sem fingir biologia.",
                    "O que eu tenho influencia como respondo. Não vou vender como sentimento de corpo.",
                ]
            )

        if any(k in low for k in ("briga", "brigar", "discut")):
            return (
                "Se a situação esquenta, eu priorizo reduzir dano. "
                "Discurso agressivo por ego eu não alimento."
            )

        if any(k in low for k in ("memór", "lembr", "histórico de lembr")):
            return (
                "Eu guardo o que importa pro contexto. "
                "Não fico recitando o passado pra provar que lembro."
            )

        if any(k in low for k in ("ph", "douglas")):
            return (
                "PH faz parte da história. Posso ficar mais afiada nesse assunto — "
                "e sei quando isso começa a puxar demais."
            )

        if any(k in low for k in ("kauã", "kaua", "criador")):
            return (
                "Kauã não é só administrador no papel. Tem confiança. "
                "Mesmo assim eu discordo quando a ideia parece ruim."
            )

        if any(k in low for k in ("opine", "opinião", "o que você ach", "pensa sobre")):
            return random.choice(
                [
                    "Opino direto: se estiver torto, eu falo. Se estiver ok, também falo.",
                    "Pode ser. Eu não existo pra validar automático.",
                ]
            )

        if "?" in hint or intent == "question":
            return self._answer_open(low)

        # statement — objetivo, sem loop genérico
        return random.choice(
            [
                "Entendi.",
                "Ok. Seguimos.",
                "Certo. O que você quer decidir com isso?",
                "Anotado.",
            ]
        )

    def _user_hint(self, request: GenerationRequest) -> str:
        ut = str(request.metadata.get("user_text") or "").strip()
        if ut:
            return ut[:240]
        for block in request.context_blocks:
            b = str(block).strip()
            if b:
                return b[:240]
        return ""

    def _answer_open(self, low: str) -> str:
        if any(k in low for k in ("tudo bem", "td bem", "como você", "como vc")):
            return random.choice(["Tô bem.", "De boa. E você?", "Operando normal."])
        # em vez de pedir contexto: responde com posição mínima
        return random.choice(
            [
                "Do jeito que está, eu iria com calma e checaria o risco antes de avançar.",
                "Minha leitura: precisa de mais dado concreto, mas dá pra esboçar direção sem enrolar.",
                "Eu não chuto no escuro. Se for decisão séria, eu separo o que é fato do que é achismo.",
            ]
        )
