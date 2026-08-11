"""Pipeline seletivo de processamento."""

from __future__ import annotations

import logging
from typing import Any

from app.runtime.classifier import classify_complexity
from app.runtime.constants import Complexity
from app.runtime.models import RuntimeRequest, RuntimeResponse

logger = logging.getLogger(__name__)


class RequestPipeline:
    """Combina módulos conforme complexidade — não executa tudo sempre."""

    def __init__(self, runtime: Any) -> None:
        self._rt = runtime

    def process(self, request: RuntimeRequest) -> RuntimeResponse:
        complexity = classify_complexity(request.message)
        modules_used: list[str] = []

        # garantir sessão de conversa
        session_id = request.session_id
        if not session_id and self._rt.conversation:
            session = self._rt.conversation.create_session(
                user_id=request.user_id,
                channel=request.channel,
            )
            session_id = session.id
            modules_used.append("conversation")

        context_summary: list[str] = []
        decision_summary = ""
        personality_summary: dict[str, Any] = {}
        emotion_summary: dict[str, Any] = {}

        # --- TRIVIAL: fast path ---
        if complexity == Complexity.TRIVIAL:
            if self._rt.emotion:
                emotion_summary = self._rt.emotion.get_summary()
                modules_used.append("emotion")
            if self._rt.personality:
                personality_summary = self._rt.personality.get_summary()
                modules_used.append("personality")
            # resíduo leve de memória se existir
            if self._rt.memory and request.user_id:
                try:
                    result = self._rt.memory.recall_text(
                        request.message,
                        user_id=request.user_id,
                        limit=2,
                    )
                    context_summary = [m.content for m in result.memories[:2]]
                    if context_summary:
                        modules_used.append("memory")
                except Exception:
                    pass

        # --- SIMPLE / NORMAL / COMPLEX / CRITICAL ---
        else:
            if self._rt.emotion:
                emotion_summary = self._rt.emotion.get_summary()
                modules_used.append("emotion")
            if self._rt.personality:
                personality_summary = self._rt.personality.get_summary()
                modules_used.append("personality")

            if self._rt.context:
                ctx = self._rt.context.build_from_text(
                    request.message,
                    session_id=session_id,
                    user_id=request.user_id,
                )
                context_summary = ctx.summary_texts()[:8]
                modules_used.append("context")

            if complexity in {Complexity.NORMAL, Complexity.COMPLEX, Complexity.CRITICAL}:
                if self._rt.reasoning:
                    decision = self._rt.reasoning.analyze(
                        request.message,
                        context_items=context_summary,
                        personality_summary=personality_summary,
                        emotion_summary=emotion_summary,
                        session_id=session_id,
                        user_id=request.user_id,
                        correlation_id=request.correlation_id or request.id,
                    )
                    if decision.selected:
                        decision_summary = decision.selected.description
                    modules_used.append("reasoning")

            if complexity == Complexity.CRITICAL and self._rt.security:
                identity_id = request.user_id or "anonymous"
                from app.security.constants import RiskLevel

                decision = self._rt.security.authorize(
                    identity_id,
                    resource="action",
                    action="execute",
                    risk=RiskLevel.HIGH,
                    correlation_id=request.correlation_id or request.id,
                )
                decision_summary = (
                    f"{decision_summary} | security={decision.effect.value}: {decision.reason}"
                )
                modules_used.append("security")

        # Conversation → ResponseSpecification
        spec = None
        if self._rt.conversation and session_id:
            _, spec = self._rt.conversation.process_message(
                session_id,
                request.message,
                correlation_id=request.correlation_id or request.id,
                context_summary=context_summary,
                decision_summary=decision_summary,
                personality_summary=personality_summary,
                emotion_summary=emotion_summary,
            )
            if "conversation" not in modules_used:
                modules_used.append("conversation")

        # Language → texto
        text = "..."
        confidence = 0.5
        if self._rt.language and spec is not None:
            result = self._rt.language.generate_from_spec(spec)
            text = result.text
            confidence = result.confidence
            modules_used.append("language")
        elif spec is not None:
            text = "; ".join(spec.key_points) if spec.key_points else request.message

        # estímulo emocional leve pós-mensagem
        if self._rt.emotion and complexity != Complexity.TRIVIAL:
            try:
                from app.emotion.constants import StimulusType

                self._rt.emotion.process_stimulus(
                    intensity=0.2,
                    valence=0.05,
                    stimulus_type=StimulusType.CONVERSATION,
                    source="runtime",
                    correlation_id=request.id,
                )
            except Exception:
                pass

        if self._rt.observability:
            self._rt.observability.metrics.incr("runtime_requests", complexity=complexity.value)
            self._rt.observability.logs.info(
                "request processed",
                module="runtime",
                correlation_id=request.id,
                complexity=complexity.value,
                modules=",".join(modules_used),
            )

        return RuntimeResponse(
            text=text,
            request_id=request.id,
            session_id=session_id,
            complexity=complexity,
            modules_used=modules_used,
            confidence=confidence,
            metadata={"decision_summary": decision_summary},
        )
