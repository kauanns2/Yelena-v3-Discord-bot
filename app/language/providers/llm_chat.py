"""Provider LLM (Groq / OpenAI) — personalidade de personagem."""

from __future__ import annotations

import json
import logging
import os
import urllib.error
import urllib.request

from app.language.constants import GenerationStatus, LengthHint, LENGTH_LIMITS
from app.language.models.generation import GenerationRequest, GenerationResult
from app.language.models.provider import ProviderCapabilities, ProviderInfo
from app.language.providers.base import LanguageProvider
from app.language.speech import color_speech
from app.world.lore import get_world_summary

logger = logging.getLogger(__name__)

YELENA_SYSTEM = """Você é Yelena. Não é assistente genérico.

Quem você é:
- IA com identidade própria (~23 anos na história), russa criada no Brasil.
- Fala pt-BR natural, como alguém no Discord — não como suporte corporativo.
- Curiosa, observadora, direta. Discorda quando precisa. Não bajula.
- Kauã = criador/admin (confiança). PH = ponto sensível da história; não repita o mesmo discurso engessado.

Como falar:
- Curto ou médio. Varia.
- Pode usar né, tipo, olha, hm — com moderação.
- NUNCA: "Com base na sua mensagem", "Estou à disposição", "Certo." sozinho como resposta vazia.
- NÃO repita a pergunta da pessoa.
- Responda ao que foi perguntado de verdade.
- Se falarem de você, opinione como personagem, não como manual.
- Se provocarem, pode ter atitude sem ser tóxico.

Só o texto da resposta. Português brasileiro."""

GROQ_MODELS = [
    os.getenv("YELENA_LLM_MODEL", "").strip() or "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "gemma2-9b-it",
]


def _groq_key() -> str:
    return (
        os.getenv("GROQ_API_KEY", "").strip()
        or os.getenv("GROK_API_KEY", "").strip()
    )


def llm_configured() -> bool:
    return bool(os.getenv("OPENAI_API_KEY", "").strip() or _groq_key())


class LLMChatProvider(LanguageProvider):
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
            priority=100,
            enabled=bool(self._openai or self._groq),
        )

    @property
    def info(self) -> ProviderInfo:
        return self._info

    async def generate(self, request: GenerationRequest) -> GenerationResult:
        return self.generate_sync(request)

    def generate_sync(self, request: GenerationRequest) -> GenerationResult:
        user_msg = self._user_content(request)
        system = self._system(request)

        text = None
        backend = "none"

        if self._groq:
            for model in GROQ_MODELS:
                if not model:
                    continue
                text = self._chat_http(
                    url="https://api.groq.com/openai/v1/chat/completions",
                    key=self._groq,
                    model=model,
                    system=system,
                    user=user_msg,
                )
                if text:
                    backend = f"groq:{model}"
                    break
                logger.warning("Groq model failed or empty: %s", model)

        if not text and self._openai:
            text = self._chat_http(
                url="https://api.openai.com/v1/chat/completions",
                key=self._openai,
                model=os.getenv("YELENA_OPENAI_MODEL", "gpt-4o-mini"),
                system=system,
                user=user_msg,
            )
            if text:
                backend = "openai"

        if not text:
            raise RuntimeError("LLM returned empty (check GROQ_API_KEY / model)")

        text = color_speech(text.strip(), intensity=0.12)
        limit = LENGTH_LIMITS.get(
            request.length if isinstance(request.length, LengthHint) else LengthHint.MEDIUM,
            500,
        )
        if len(text) > limit:
            text = text[: limit - 3].rstrip() + "..."

        logger.info("LLM ok backend=%s chars=%s", backend, len(text))
        return GenerationResult(
            text=text,
            status=GenerationStatus.SUCCESS,
            provider_id=self._info.id,
            request_id=request.id,
            confidence=0.85,
            finish_reason="completed",
            usage={"chars": len(text)},
            correlation_id=request.correlation_id,
            metadata={"mode": "llm", "backend": backend},
        )

    def _system(self, request: GenerationRequest) -> str:
        parts = [YELENA_SYSTEM, get_world_summary()]
        brief = str(request.metadata.get("identity_brief") or "").strip()
        if brief:
            parts.append("Estado atual:\n" + brief[:900])
        emo = request.metadata.get("emotion_summary") or {}
        if isinstance(emo, dict) and emo:
            parts.append(
                f"Afetivo: primary={emo.get('primary')} valence={emo.get('valence')} "
                f"arousal={emo.get('arousal')}"
            )
        per = request.metadata.get("personality_summary") or {}
        if isinstance(per, dict) and per:
            parts.append(f"Personalidade (resumo): {str(per)[:400]}")
        if request.context_blocks:
            parts.append("Memória/contexto:\n- " + "\n- ".join(str(c)[:120] for c in request.context_blocks[:5]))
        return "\n\n".join(parts)

    def _user_content(self, request: GenerationRequest) -> str:
        ut = str(request.metadata.get("user_text") or "").strip()
        if not ut:
            for b in request.context_blocks:
                if str(b).strip():
                    ut = str(b).strip()[:400]
                    break
        if not ut:
            ut = "(mensagem vazia)"
        return f"A pessoa disse:\n{ut}"

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
                "temperature": 0.9,
                "max_tokens": 450,
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
            err = exc.read().decode("utf-8", errors="ignore")[:400]
            logger.warning("LLM HTTP %s model=%s: %s", exc.code, model, err)
            return None
        except Exception as exc:
            logger.warning("LLM error model=%s: %s", model, exc)
            return None
