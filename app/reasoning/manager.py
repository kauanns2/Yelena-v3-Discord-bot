"""Reasoning Manager."""

from __future__ import annotations

import logging
import time
from typing import Any

from app.reasoning.constants import StrategyType, DecisionStatus
from app.reasoning.engine import ReasoningEngine
from app.reasoning.models.problem import Problem, Goal, Constraint
from app.reasoning.models.decision import Decision
from app.reasoning.models.explanation import Explanation
from app.reasoning.models.plan import Plan, ActionProposal

logger = logging.getLogger(__name__)


class ReasoningManager:
    """API principal do Reasoning System.

    Produz Decision estruturada. Não gera texto final. Não executa ações.
    """

    def __init__(self) -> None:
        self._engine = ReasoningEngine()
        self._started = False
        self._last_decision: Decision | None = None
        self._metrics = {
            "problems_analyzed": 0,
            "decisions_made": 0,
            "needs_info": 0,
            "actions_proposed": 0,
        }

    @property
    def is_started(self) -> bool:
        return self._started

    def start(self) -> None:
        self._started = True
        logger.info("reasoning system started")

    def stop(self) -> None:
        self._started = False

    def analyze(
        self,
        description: str,
        *,
        goals: list[str] | None = None,
        constraints: list[str] | None = None,
        context_items: list[str] | None = None,
        personality_summary: dict[str, Any] | None = None,
        emotion_summary: dict[str, Any] | None = None,
        session_id: str | None = None,
        user_id: str | None = None,
        correlation_id: str | None = None,
        strategy: StrategyType = StrategyType.DIRECT,
    ) -> Decision:
        problem = Problem(
            description=description,
            goals=[Goal(description=g) for g in (goals or [])],
            constraints=[Constraint(description=c) for c in (constraints or [])],
            context_summary=" | ".join((context_items or [])[:5]),
            session_id=session_id,
            user_id=user_id,
            correlation_id=correlation_id,
        )

        decision = self._engine.analyze(
            problem,
            context_items=context_items,
            personality_summary=personality_summary,
            emotion_summary=emotion_summary,
            strategy=strategy,
        )

        explanation = self._engine.build_explanation(decision, problem)
        decision.explanation_id = explanation.id
        decision.metadata["explanation"] = explanation.to_dict()

        plan = self._engine.build_plan(decision, description[:100])
        decision.plan_id = plan.id
        decision.metadata["plan"] = plan.to_dict()

        action = self._engine.propose_action(decision)
        if action:
            decision.metadata["action_proposal"] = action.to_dict()
            self._metrics["actions_proposed"] += 1

        self._last_decision = decision
        self._metrics["problems_analyzed"] += 1
        if decision.status == DecisionStatus.DECIDED:
            self._metrics["decisions_made"] += 1
        elif decision.status == DecisionStatus.NEEDS_INFO:
            self._metrics["needs_info"] += 1

        logger.debug(
            "decision made",
            extra={
                "status": decision.status.value,
                "confidence": decision.confidence,
                "risk": decision.risk.value,
            },
        )
        return decision

    def get_last_decision(self) -> Decision | None:
        return self._last_decision

    def health(self) -> dict[str, Any]:
        return {
            "status": "healthy" if self._started else "stopped",
            "metrics": dict(self._metrics),
        }
