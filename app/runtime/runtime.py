"""Yelena Runtime — orquestração dos módulos."""

from __future__ import annotations

import logging
from typing import Any

from app.runtime.constants import RuntimeState
from app.runtime.errors import RuntimeNotStartedError
from app.runtime.models import RuntimeRequest, RuntimeResponse
from app.runtime.pipeline import RequestPipeline

logger = logging.getLogger(__name__)


class YelenaRuntime:
    """Runtime da Yelena V3.

    Compõe e coordena módulos. Não é God Object de domínio.
    """

    def __init__(self) -> None:
        self.state = RuntimeState.CREATED

        # módulos (preenchidos no bootstrap)
        self.configuration: Any = None
        self.neural: Any = None
        self.event_bus: Any = None
        self.memory: Any = None
        self.knowledge: Any = None
        self.context: Any = None
        self.emotion: Any = None
        self.personality: Any = None
        self.reasoning: Any = None
        self.conversation: Any = None
        self.language: Any = None
        self.actions: Any = None
        self.security: Any = None
        self.observability: Any = None

        self._pipeline: RequestPipeline | None = None

    def bootstrap(self) -> None:
        """Instancia módulos na ordem segura de dependência."""
        self.state = RuntimeState.STARTING

        from app.configuration import ConfigurationManager
        from app.neural import NeuralWebManager
        from app.event_bus import EventBus
        from app.memory import MemoryManager
        from app.knowledge import KnowledgeManager
        from app.context import ContextManager
        from app.emotion import EmotionManager
        from app.personality import PersonalityManager
        from app.reasoning import ReasoningManager
        from app.conversation import ConversationManager
        from app.language import LanguageManager
        from app.actions import ActionManager
        from app.security import SecurityManager
        from app.observability import ObservabilityManager

        self.configuration = ConfigurationManager()
        self.configuration.load()

        self.observability = ObservabilityManager()
        self.security = SecurityManager()
        self.event_bus = EventBus()
        self.neural = NeuralWebManager()
        self.memory = MemoryManager()
        self.knowledge = KnowledgeManager()
        self.context = ContextManager(
            memory_manager=self.memory,
            knowledge_manager=self.knowledge,
            neural_manager=self.neural,
        )
        self.emotion = EmotionManager()
        self.personality = PersonalityManager()
        self.reasoning = ReasoningManager()
        self.conversation = ConversationManager()
        self.language = LanguageManager()
        self.actions = ActionManager()

        # wire health checkers
        for name, mod in [
            ("configuration", self.configuration),
            ("security", self.security),
            ("memory", self.memory),
            ("knowledge", self.knowledge),
            ("context", self.context),
            ("emotion", self.emotion),
            ("personality", self.personality),
            ("reasoning", self.reasoning),
            ("conversation", self.conversation),
            ("language", self.language),
            ("actions", self.actions),
            ("event_bus", self.event_bus),
            ("neural", self.neural),
        ]:
            if hasattr(mod, "health"):
                self.observability.register_health(name, mod.health)

        self._pipeline = RequestPipeline(self)
        logger.info("runtime bootstrap complete")

    def start(self) -> None:
        if self.state == RuntimeState.CREATED:
            self.bootstrap()

        # start order: infra → cognitive → interface
        for mod in [
            self.observability,
            self.security,
            self.event_bus,
            self.neural,
            self.memory,
            self.knowledge,
            self.context,
            self.emotion,
            self.personality,
            self.reasoning,
            self.conversation,
            self.language,
            self.actions,
        ]:
            if mod and hasattr(mod, "start"):
                mod.start()

        self.state = RuntimeState.READY
        if self.observability:
            self.observability.logs.info("Yelena runtime ready", module="runtime")
        logger.info("Yelena runtime ready")

    def stop(self) -> None:
        self.state = RuntimeState.STOPPING
        for mod in [
            self.actions,
            self.language,
            self.conversation,
            self.reasoning,
            self.personality,
            self.emotion,
            self.context,
            self.knowledge,
            self.memory,
            self.neural,
            self.event_bus,
            self.security,
            self.observability,
        ]:
            if mod and hasattr(mod, "stop"):
                try:
                    mod.stop()
                except Exception:
                    logger.exception("error stopping module")
        self.state = RuntimeState.STOPPED
        logger.info("Yelena runtime stopped")

    def process(
        self,
        message: str,
        *,
        user_id: str | None = None,
        session_id: str | None = None,
        channel: str = "default",
        correlation_id: str | None = None,
    ) -> RuntimeResponse:
        if self.state not in {RuntimeState.READY, RuntimeState.DEGRADED}:
            raise RuntimeNotStartedError(
                f"Runtime not ready: {self.state.value}",
                context={"state": self.state.value},
            )
        assert self._pipeline is not None
        request = RuntimeRequest(
            message=message,
            user_id=user_id,
            session_id=session_id,
            channel=channel,
            correlation_id=correlation_id,
        )
        return self._pipeline.process(request)

    def health(self) -> dict[str, Any]:
        report = None
        if self.observability:
            report = self.observability.check_health()
        return {
            "state": self.state.value,
            "health": report.to_dict() if report else {},
        }
