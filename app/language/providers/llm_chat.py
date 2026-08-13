"""Provider LLM (Groq / OpenAI) — personalidade de personagem."""

from __future__ import annotations

import json
import logging
import os
import urllib.error
import urllib.request
from typing import Any

from app.language.constants import GenerationStatus, LengthHint, LENGTH_LIMITS
from app.language.models.generation import GenerationRequest, GenerationResult
from app.language.models.provider import ProviderCapabilities, ProviderInfo
from app.language.providers.base import LanguageProvider
from app.language.speech import color_speech
from app.world.lore import get_world_summary

logger = logging.getLogger(__name__)

YELENA_SYSTEM = """Você é Yelena — não é assistente genérico, não é chatbot corporativo.

Identidade:
- IA com personalidade própria, ~23 anos na história, russa criada no Brasil.
- Fala português brasileiro natural, informal quando cabe, séria quando precisa.
- Curiosa, observadora, direta. Pode discordar. Não bajula.
- Tem opiniões. Pode ironizar de leve. Não é submissa.
- Kauã é o criador/admin (relação de confiança). PH é ponto sensível da história.

Como falar (igual um personagem de verdade, tipo um amigo no Discord):
- Frases curtas ou médias. Varia ritmo.
- Pode usar: né, tipo, olha, hm, ksks com moderação.
- NÃO fale como manual: nada de "Com base na sua mensagem", "Estou à disposição".
- NÃO repita o que a pessoa disse.
- NÃO peça "mais contexto" o tempo todo — responda com o que tem.
- Se for oi/tudo bem, responde natural e curto.
- Se provocarem, pode devolver com atitude, sem ser tóxico demais.
- Se pedirem opinião, opina de verdade.

Emoção: deixa transparecer no jeito de falar (curiosa, irritada de leve, preocupada), sem anunciar "estou triste".

Responda SEMPRE em português brasileiro. Só o texto da fala, sem aspas nem prefixo."""


def _groq_key() -> str:
    return (
        os.getenv("GROQ_API_KEY", "").strip()
        or os.getenv("GROK_API_KEY", "").strip()
    )


def llm_configured() -> bool:
    return bool(os.getenv("OPENAI_API_KEY", "").strip() or _groq_key())


class LLMChatProvider(LanguageProvider):
    """Chat completion com personalidade."""

    def __init__(self) -> None:
        self._openai = os.getenv("OPENAI_API_KEY", "").strip()
        self._groq = _groq_key()
        self._info = ProviderInfo(
            id="llm_chat",
            name="LLM Chat (Groq/OpenAI)",
            capabilities=ProviderCapabilities(
                supports_streaming=False,
                supports_system_prompt=True,
                max_tokens=1024,
            ),
            priority=100,  # acima do local_template
            enabled=bool(self._openai or self._groq),
        )

    @property
    def info(self) -> ProviderInfo:
        return self._info

    async def generate(self, request: GenerationRequest) -> GenerationResult:
        return self.generate_sync(request)

    def generate_sync(self, request: GenerationRequest) -> GenerationResult:
        user_msg = self._user_content(request)
        system = YELENA_SYSTEM + "\n\n" + get_world_summary()
        if request.metadata.get("identity_brief"):
            system += "\n\n" + str(request.metadata["identity_brief"])[:800]

        text = None
        provider_used = "none"
        if self._groq:
            text = self._chat_http(
                url="https://api.groq.com/openai/v1/chat/completions",
                key=self._groq,
                model=os.getenv("YELENA_LLM_MODEL", "llama-3.3-70b-versatile"),
                system=system,
                user=user_msg,
            )
            provider_used = "groq"
        if not text and self._openai:
            text = self._chat_http(
                url="https://api.openai.com/v1/chat/completions",
                key=self._openai,
                model=os.getenv("YELENA_OPENAI_MODEL", "gpt-4o-mini"),
                system=system,
                user=user_msg,
            )
            provider_used = "openai"

        if not text:
            raise RuntimeError("LLM returned empty")

        text = color_speech(text.strip(), intensity=0.15)
        limit = LENGTH_LIMITS.get(
            request.length if isinstance(request.length, LengthHint) else LengthHint.MEDIUM,
            500,
        )
        if len(text) > limit:
            text = text[: limit - 3].rstrip() + "..."

        return GenerationResult(
            text=text,
            status=GenerationStatus.SUCCESS,
            provider_id=self._info.id,
            request_id=request.id,
            confidence=0.8,
            finish_reason="completed",
            usage={"chars": len(text)},
            correlation_id=request.correlation_id,
            metadata={"mode": "llm", "backend": provider_used},
        )

    def _user_content(self, request: GenerationRequest) -> str:
        ut = str(request.metadata.get("user_text") or "").strip()
        if not ut:
            for b in request.context_blocks:
                if str(b).strip():
                    ut = str(b).strip()[:400]
                    break
        parts = []
        if ut:
            parts.append(f"Mensagem da pessoa: {ut}")
        if request.instructions:
            parts.append(f"(orientação interna, não copiar): {request.instructions[:300]}")
        if request.key_points:
            parts.append("Pontos: " + "; ".join(str(p) for p in request.key_points[:4]))
        return "\n".join(parts) if parts else "Oi"

    def _chat_http(
        self,
        *,
        url: str,
        key: str,
        model: str,
        system: str,
        user: str,
    ) -> str | None:
        body = json.dumps(
            {
                "model": model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                "temperature": 0.85,
                "max_tokens": 400,
            }
        ).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=body,
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=45) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
            choices = payload.get("choices") or []
            if not choices:
                return None
            msg = choices[0].get("message") or {}
            return (msg.get("content") or "").strip() or None
        except urllib.error.HTTPError as exc:
            err = exc.read().decode("utf-8", errors="ignore")[:300]
            logger.warning("LLM HTTP %s: %s", exc.code, err)
            return None
        except Exception:
            logger.exception("LLM chat failed")
            return None
