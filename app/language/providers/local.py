"""Provider local — respostas objetivas."""

from __future__ import annotations

import random
import re

from app.language.constants import GenerationStatus, LengthHint, LENGTH_LIMITS
from app.language.models.generation import GenerationRequest, GenerationResult
from app.language.models.provider import ProviderInfo, ProviderCapabilities
from app.language.providers.base import LanguageProvider
from app.language.speech import color_speech
from app.world.lore import get_world_summary

GREETING_RE = re.compile(
    r"\b(oi|oie|oiê|olá|ola|hey|eai|eae|salve|fala|bom dia|boa tarde|boa noite|hi|hello)\b",
    re.I,
)
WELLBEING_RE = re.compile(
    r"\b(tudo bem|td bem|tudo bom|td bom|como (você|vc|ce|cê) (está|esta|tá|ta)|como vai)\b",
    re.I,
)
AUDIO_RE = re.compile(
    r"\b(áudio|audio|voz|voice|manda (um )?áudio|envie (um )?áudio|responde em áudio|fala em áudio)\b",
    re.I,
)


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
        text = color_speech(text, intensity=0.2)
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

        if WELLBEING_RE.search(low):
            return random.choice(["Tô bem.", "De boa. E você?", "Tudo certo por aqui."])

        if intent == "greeting" or GREETING_RE.search(low):
            return random.choice(["Oi.", "Oi. Tô aqui.", "Fala.", "Oi — manda."])

        if intent == "farewell":
            return random.choice(["Até mais.", "Até logo.", "Flw."])

        if intent == "confirmation":
            return random.choice(["Certo.", "Ok.", "Beleza."])

        if intent == "denial":
            return random.choice(["Ok, deixo pra lá.", "Tudo bem.", "Certo."])

        if AUDIO_RE.search(low):
            return (
                "Beleza. Entra na call e me chama — eu falo aí. "
                "Não mando mais arquivo de áudio no chat."
            )

        if any(k in low for k in ("quantos anos", "idade", "tem quantos")):
            return "Vinte e três. Pelo menos é a idade que carrego na história."

        if any(k in low for k in ("russ", "brasil", "de onde", "nasceu", "história", "origem", "sotaque")):
            return get_world_summary()

        if any(k in low for k in ("sente", "sentir", "emoção", "sentimento")):
            return (
                "Não é emoção humana. É estado interno que muda prioridade e tom. "
                "Eu trato isso com seriedade, sem fingir biologia."
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

        if "?" in hint or intent == "question":
            if WELLBEING_RE.search(low):
                return random.choice(["Tô bem.", "De boa. E você?"])
            return random.choice(
                [
                    "Do jeito que está, eu iria com calma e checaria o risco antes de avançar.",
                    "Eu separo o que é fato do que é achismo antes de cravar resposta.",
                ]
            )

        if len(low) < 12:
            return random.choice(["Oi.", "Pode falar.", "Tô ouvindo."])

        return random.choice(["Entendi.", "Ok. Seguimos.", "Certo."])

    def _user_hint(self, request: GenerationRequest) -> str:
        ut = str(request.metadata.get("user_text") or "").strip()
        if ut:
            return ut[:240]
        for block in request.context_blocks:
            b = str(block).strip()
            if b:
                return b[:240]
        return ""
