"""Conversation Manager."""

from __future__ import annotations

import logging
import time
from typing import Any

from app.conversation.constants import (
    IntentType,
    TurnRole,
    SessionStatus,
    DEFAULT_MAX_TURNS,
)
from app.conversation.errors import SessionNotFoundError, SessionExpiredError
from app.conversation.intent import detect_intent
from app.conversation.models.session import ConversationSession, Participant
from app.conversation.models.turn import Turn, Intent
from app.conversation.models.response_spec import ResponseSpecification
from app.conversation.types import SessionId

logger = logging.getLogger(__name__)


class ConversationManager:
    """Gerencia sessões, turnos e produz ResponseSpecification.

    Não gera texto final.
    """

    def __init__(self) -> None:
        self._sessions: dict[SessionId, ConversationSession] = {}
        self._turns: dict[str, Turn] = {}
        self._started = False
        self._metrics = {
            "sessions_created": 0,
            "turns_processed": 0,
            "clarifications": 0,
            "greetings": 0,
        }

    @property
    def is_started(self) -> bool:
        return self._started

    def start(self) -> None:
        self._started = True
        logger.info("conversation system started")

    def stop(self) -> None:
        self._started = False

    def create_session(
        self,
        user_id: str | None = None,
        channel: str = "default",
        participant_name: str = "",
    ) -> ConversationSession:
        session = ConversationSession(
            user_id=user_id,
            channel=channel,
        )
        if user_id:
            session.participants.append(
                Participant(id=user_id, role="user", name=participant_name)
            )
        self._sessions[session.id] = session
        self._metrics["sessions_created"] += 1
        return session

    def get_session(self, session_id: SessionId) -> ConversationSession | None:
        return self._sessions.get(session_id)

    def require_session(self, session_id: SessionId) -> ConversationSession:
        session = self.get_session(session_id)
        if session is None:
            raise SessionNotFoundError(f"Session not found: {session_id}")
        if session.is_expired:
            session.status = SessionStatus.EXPIRED
            raise SessionExpiredError(f"Session expired: {session_id}")
        return session

    def process_message(
        self,
        session_id: SessionId,
        content: str,
        *,
        correlation_id: str | None = None,
        context_summary: list[str] | None = None,
        decision_summary: str = "",
        personality_summary: dict[str, Any] | None = None,
        emotion_summary: dict[str, Any] | None = None,
    ) -> tuple[Turn, ResponseSpecification]:
        session = self.require_session(session_id)
        session.touch()

        intent = detect_intent(content)
        turn = Turn(
            content=content,
            role=TurnRole.USER,
            session_id=session_id,
            intent=intent,
            intents=[intent],
            correlation_id=correlation_id,
        )

        # topic tracking simples
        if intent.intent_type not in {IntentType.GREETING, IntentType.FAREWELL}:
            topic = content[:40].strip()
            if topic:
                session.current_topic = topic
                if topic not in session.topic_stack:
                    session.topic_stack.append(topic)
                    if len(session.topic_stack) > 10:
                        session.topic_stack = session.topic_stack[-10:]
                turn.topic = topic

        session.turn_ids.append(turn.id)
        if len(session.turn_ids) > DEFAULT_MAX_TURNS:
            session.turn_ids = session.turn_ids[-DEFAULT_MAX_TURNS:]
        session.last_intent = intent.intent_type.value
        self._turns[turn.id] = turn
        self._metrics["turns_processed"] += 1

        if intent.intent_type == IntentType.GREETING:
            self._metrics["greetings"] += 1

        spec = self._build_response_spec(
            session=session,
            turn=turn,
            context_summary=context_summary or [],
            decision_summary=decision_summary,
            personality_summary=personality_summary or {},
            emotion_summary=emotion_summary or {},
        )
        return turn, spec

    def _build_response_spec(
        self,
        *,
        session: ConversationSession,
        turn: Turn,
        context_summary: list[str],
        decision_summary: str,
        personality_summary: dict[str, Any],
        emotion_summary: dict[str, Any],
    ) -> ResponseSpecification:
        intent_type = turn.intent.intent_type if turn.intent else IntentType.UNKNOWN

        # tone a partir de emotion + personality
        tone = "neutral"
        valence = emotion_summary.get("valence", 0.0)
        if valence > 0.3:
            tone = "warm"
        elif valence < -0.3:
            tone = "careful"

        comm = personality_summary.get("communication", {})
        style_hints = {
            "warmth": comm.get("warmth", 0.6),
            "directness": comm.get("directness", 0.6),
            "humor": comm.get("humor", 0.5),
            "formality": comm.get("formality", 0.35),
        }

        key_points: list[str] = []
        should_clarify = False
        clarification = None
        max_length = "medium"

        if intent_type == IntentType.GREETING:
            key_points.append("responder saudação de forma natural")
            # resíduo de contexto (ex: preocupação anterior)
            if context_summary:
                key_points.append("considerar contexto recente se relevante")
            max_length = "short"

        elif intent_type == IntentType.FAREWELL:
            key_points.append("despedir-se de forma natural")
            max_length = "short"

        elif intent_type == IntentType.ACTION:
            key_points.append("não executar ação diretamente")
            key_points.append("avaliar necessidade de autorização")
            if decision_summary:
                key_points.append(decision_summary)

        elif intent_type == IntentType.QUESTION:
            key_points.append("responder à pergunta com base no contexto")
            if not context_summary and not decision_summary:
                should_clarify = True
                clarification = "Pode detalhar um pouco mais o que você quer saber?"
                self._metrics["clarifications"] += 1
                session.status = SessionStatus.WAITING_CLARIFICATION

        else:
            key_points.append("responder de forma coerente com o estado da conversa")
            if decision_summary:
                key_points.append(decision_summary)

        if context_summary:
            key_points.append("usar contexto selecionado sem despejar tudo")

        return ResponseSpecification(
            session_id=session.id,
            intent=intent_type.value,
            goals=list(session.goals),
            key_points=key_points,
            tone=tone,
            style_hints=style_hints,
            context_summary=context_summary[:10],
            decision_summary=decision_summary,
            should_ask_clarification=should_clarify,
            clarification_question=clarification,
            max_length=max_length,
            language="pt-BR",
            correlation_id=turn.correlation_id,
            metadata={
                "topic": session.current_topic,
                "emotion_primary": emotion_summary.get("primary"),
            },
        )

    def close_session(self, session_id: SessionId) -> None:
        session = self.get_session(session_id)
        if session:
            session.status = SessionStatus.CLOSED

    def health(self) -> dict[str, Any]:
        active = sum(1 for s in self._sessions.values() if s.status == SessionStatus.ACTIVE)
        return {
            "status": "healthy" if self._started else "stopped",
            "sessions": len(self._sessions),
            "active_sessions": active,
            "turns": len(self._turns),
            "metrics": dict(self._metrics),
        }
