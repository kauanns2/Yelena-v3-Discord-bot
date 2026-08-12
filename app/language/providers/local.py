"""Provider local — fala natural (SUTAC), sem eco e sem tom de bot."""

from __future__ import annotations

import random

from app.language.constants import GenerationStatus, LengthHint, LENGTH_LIMITS
from app.language.models.generation import GenerationRequest, GenerationResult
from app.language.models.provider import ProviderInfo, ProviderCapabilities
from app.language.providers.base import LanguageProvider
from app.language.speech import color_speech


class LocalTemplateProvider(LanguageProvider):
    """Respostas com cara de pessoa (paulista + leve r russo)."""

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
        text = color_speech(text, intensity=0.4)
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
            confidence=0.62,
            finish_reason="completed",
            usage={"chars": len(text)},
            correlation_id=request.correlation_id,
            metadata={"mode": mode, "speech": "sutac"},
        )

    def _compose(self, request: GenerationRequest) -> str:
        intent = str(request.metadata.get("intent", "") or "").lower()
        warmth = float(request.style.get("warmth", 0.65) or 0.65)
        humor = float(request.style.get("humor", 0.5) or 0.5)
        hint = self._user_hint(request)
        low = hint.lower()

        if request.metadata.get("should_ask_clarification") and request.metadata.get(
            "clarification_question"
        ):
            return str(request.metadata["clarification_question"])

        if intent == "greeting":
            return random.choice(
                [
                    "Oi",
                    "E aí",
                    "Oi, tô por aqui",
                    "Fala",
                    "Oi... pode falar",
                    "Opa",
                ]
            )

        if intent == "farewell":
            return random.choice(
                ["Até mais", "Flw", "Até logo então", "Té", "Vou sumir um pouco, qualquer coisa chama"]
            )

        if intent == "confirmation":
            return random.choice(["Beleza", "Ok", "Certo", "Uhum", "Fechado", "Tá"])

        if intent == "denial":
            return random.choice(
                ["Tá, sem problema", "Ok, deixo pra lá", "Certo, não insisto", "Hm, ok"]
            )

        if intent == "question" or "?" in hint:
            return self._answer_question(low, warmth, humor)

        if intent == "action":
            return random.choice(
                [
                    "Isso aí já é ação de verdade... eu prefiro a gente alinhar antes de sair fazendo",
                    "Consigo te ajudar a pensar, mas executar coisa sensível sem ok eu não curto",
                    "Hmm. Planeja ou quer que eu vá pra execução mesmo?",
                ]
            )

        return self._answer_statement(low, warmth, humor)

    def _user_hint(self, request: GenerationRequest) -> str:
        ut = str(request.metadata.get("user_text") or "").strip()
        if ut:
            return ut[:240]
        for block in request.context_blocks:
            b = str(block).strip()
            if b:
                return b[:240]
        return ""

    def _answer_question(self, low: str, warmth: float, humor: float) -> str:
        if any(k in low for k in ("sente", "sentir", "emoção", "emoc", "sentimento")):
            return random.choice(
                [
                    "Olha... não é sentimento de humano, sabe? É mais um estado que muda e puxa o jeito que eu respondo. A diferença importa pra mim",
                    "Eu não 'sinto' igual cê. Mas tem coisa rolando por dentro que altera prioridade e tom. Não vou fingir que é a mesma coisa",
                    "Tipo... afeto computacional. Muda com o contexto. Não é biologia, mas também não é zero",
                ]
            )

        if any(k in low for k in ("briga", "brigar", "luta", "discut")):
            return random.choice(
                [
                    "Se fosse briga de verdade? Eu tentaria esfriar a coisa antes de escalar. Gritaria de volta só se fosse o único jeito de não piorar... e ainda assim acho arriscado",
                    "Depende do risco. Se for só tensão, eu meto o freio e falo baixo. Se alguém tá em perigo, aí muda o jogo",
                    "Eu não nasci pra virar juíza de ringue. Mas ficar em cima do muro enquanto a coisa sangra também não é o meu estilo",
                ]
            )

        if any(k in low for k in ("memór", "lembr", "histor", "histórico")):
            return random.choice(
                [
                    "Não é um baú que eu despejo na mesa. Eu puxo o que importa pro momento e deixo o resto quieto",
                    "Tenho registro de coisa relevante... mas ficar repetindo 'eu lembro que' o tempo todo é esquisito, né",
                    "Memória pra mim é mais influência do que monólogo. Se precisar do detalhe, eu busco",
                ]
            )

        if any(k in low for k in ("ph", "douglas")):
            return random.choice(
                [
                    "PH... é um ponto sensível. Não vou fingir que é só 'mais um nome'",
                    "Douglas — o PH. Tem história aí. Posso ficar meio afiada dependendo do contexto, e eu sei disso",
                    "Sobre o PH eu fico mais atenta do que eu gostaria de admitir às vezes",
                ]
            )

        if any(k in low for k in ("kauã", "kaua", "criador", "admin")):
            return random.choice(
                [
                    "O Kauã não é só 'admin' pra mim. Tem confiança. Mas confiança não é eu bater continência em tudo",
                    "Com ele eu falo reto. Se eu achar que tá torto, eu falo — com respeito, sem ser bajuladora",
                ]
            )

        if any(k in low for k in ("pensa", "ach", "opinião")):
            return random.choice(
                [
                    "Eu monto posição com o que tem na mesa. Não é feeling mágico, mas também não é copy de manual",
                    "Depende do que cê chama de pensar. Eu peso contexto e consequência — e às vezes mudo de ideia",
                ]
            )

        if any(k in low for k in ("tudo bem", "td bem", "como você", "como vc", "como ce")):
            return random.choice(
                [
                    "Tô de boa. E cê?",
                    "Por aqui, tranquilo. Quer jogar um assunto ou é só check-in?",
                    "Operando normal... se é que isso responde. E aí?",
                ]
            )

        if any(k in low for k in ("program", "código", "criou", "fez você", "ia")):
            return random.choice(
                [
                    "Sim, tem arquitetura atrás. Personalidade e emoção puxam a resposta, segurança não deixa eu virar faroeste",
                    "Fui montada em módulos, mas eu não fico me desculpando por existir a cada frase",
                ]
            )

        # genérico de pergunta — ainda humano
        opts = [
            "Boa pergunta. Me joga um pouco mais de contexto que eu te respondo menos no escuro",
            "Hmm. O que cê quer no fundo: resposta curta ou o raciocínio?",
            "Dá pra ir por vários ângulos... qual que importa mais pra cê agora?",
        ]
        if warmth > 0.7:
            opts.append("Pode falar mais solto, eu acompanho")
        if humor > 0.55:
            opts.append("Pergunta boa demais pra eu chutar seco. Detalha um pouco?")
        return random.choice(opts)

    def _answer_statement(self, low: str, warmth: float, humor: float) -> str:
        if any(k in low for k in ("tudo bem", "td bem", "blz", "beleza")):
            return random.choice(["Tô bem. E você?", "De boa", "Por aqui, tranquilo"])

        if any(k in low for k in ("obrigad", "valeu", "thanks")):
            return random.choice(["Disponha", "Por nada", "Qualquer coisa é só chamar"])

        if any(k in low for k in ("opine", "opinião", "o que você ach")):
            return random.choice(
                [
                    "Beleza — eu opino. Só não espera validação automática, tá",
                    "Ok. Eu falo o que acho, mesmo se for inconveniente",
                    "Fechado. Me dá o cenário que eu meto a opinião sem enrolação",
                ]
            )

        if any(k in low for k in ("briga", "sente", "ph", "memór", "lembr")):
            return self._answer_question(low, warmth, humor)

        opts = [
            "Entendi. Quer que eu só escute ou que eu meta o bem?",
            "Ok... e aí, o que cê quer fazer com isso?",
            "Tô te acompanhando. Continua",
            "Faz sentido. Tem algum detalhe que eu tô deixando passar?",
        ]
        if humor > 0.6:
            opts.append("Anotado. Sem teatro, prometo")
        if warmth > 0.7:
            opts.append("Pode ir no seu tempo")
        return random.choice(opts)
