"""Motor de raciocínio estruturado."""

from __future__ import annotations

import time
from typing import Any

from app.reasoning.constants import DecisionStatus, StrategyType, RiskLevel
from app.reasoning.models.problem import Problem, Goal, Constraint
from app.reasoning.models.decision import Decision, Alternative, Hypothesis
from app.reasoning.models.plan import Plan, PlanStep, ActionProposal
from app.reasoning.models.explanation import Explanation


class ReasoningEngine:
    """Produz decisões estruturadas a partir de um Problem + contexto.

    Não gera linguagem final. Não executa ações.
    """

    def analyze(
        self,
        problem: Problem,
        *,
        context_items: list[str] | None = None,
        personality_summary: dict[str, Any] | None = None,
        emotion_summary: dict[str, Any] | None = None,
        strategy: StrategyType = StrategyType.DIRECT,
    ) -> Decision:
        decision = Decision(
            problem_id=problem.id,
            status=DecisionStatus.ANALYZING,
            strategy=strategy,
            correlation_id=problem.correlation_id,
        )

        context_items = context_items or []
        personality_summary = personality_summary or {}
        emotion_summary = emotion_summary or {}

        # Detectar ambiguidades / falta de info
        if not problem.description.strip():
            decision.status = DecisionStatus.NEEDS_INFO
            decision.needs_info.append("problem_description")
            decision.ambiguity = True
            return decision

        if len(problem.description.strip()) < 3:
            decision.ambiguity = True
            decision.needs_info.append("more_detail")

        # Hipótese principal
        hypothesis = Hypothesis(
            statement=f"A intenção principal é: {problem.description[:200]}",
            confidence=0.6 if not decision.ambiguity else 0.35,
            evidence=context_items[:5],
        )
        decision.hypotheses.append(hypothesis)

        # Alternativas básicas
        alternatives = self._generate_alternatives(problem, context_items, personality_summary)
        decision.alternatives = alternatives

        if alternatives:
            selected = max(alternatives, key=lambda a: a.score)
            decision.selected = selected
            decision.confidence = selected.confidence
            decision.risk = selected.risk
            decision.uncertainty = max(0.0, 1.0 - selected.confidence)
        else:
            decision.confidence = 0.3
            decision.uncertainty = 0.7

        # Personalidade: assertiveness / caution influenciam confiança
        traits = personality_summary.get("traits", {})
        caution = traits.get("caution", 0.5)
        assertiveness = traits.get("assertiveness", 0.5)
        if caution > 0.7:
            decision.confidence *= 0.9
            decision.uncertainty = min(1.0, decision.uncertainty + 0.05)
        if assertiveness > 0.7 and decision.confidence > 0.5:
            decision.confidence = min(1.0, decision.confidence + 0.05)

        # Emoção: stress alto aumenta uncertainty
        if emotion_summary.get("stress", 0) > 0.6:
            decision.uncertainty = min(1.0, decision.uncertainty + 0.1)

        decision.status = (
            DecisionStatus.NEEDS_INFO
            if decision.needs_info and decision.confidence < 0.4
            else DecisionStatus.DECIDED
        )
        decision.completed_at = time.time()
        return decision

    def _generate_alternatives(
        self,
        problem: Problem,
        context_items: list[str],
        personality: dict[str, Any],
    ) -> list[Alternative]:
        desc = problem.description.lower()
        alternatives: list[Alternative] = []

        # Alternativa direta: responder / analisar
        alternatives.append(
            Alternative(
                description="Analisar e responder com base no contexto disponível",
                score=0.7,
                pros=["usa contexto atual", "rápido"],
                cons=["pode faltar informação"] if not context_items else [],
                risk=RiskLevel.LOW,
                confidence=0.65 if context_items else 0.45,
            )
        )

        # Se parece pedido de ação
        action_keywords = ["execute", "faça", "delete", "apague", "modifique", "rode", "implemente"]
        if any(k in desc for k in action_keywords):
            alternatives.append(
                Alternative(
                    description="Propor ação e solicitar autorização antes de executar",
                    score=0.8,
                    pros=["respeita segurança", "Pensar ≠ Executar"],
                    cons=["requer confirmação"],
                    risk=RiskLevel.MEDIUM,
                    confidence=0.75,
                )
            )
            alternatives.append(
                Alternative(
                    description="Recusar ação sem autorização suficiente",
                    score=0.6,
                    pros=["seguro"],
                    cons=["pode frustrar se autorização existir"],
                    risk=RiskLevel.LOW,
                    confidence=0.7,
                )
            )

        # Se ambíguo: pedir esclarecimento
        if len(problem.description) < 15 or "?" in problem.description:
            alternatives.append(
                Alternative(
                    description="Pedir esclarecimento antes de concluir",
                    score=0.55,
                    pros=["reduz erro"],
                    cons=["atrasa resposta"],
                    risk=RiskLevel.NONE,
                    confidence=0.6,
                )
            )

        # Ordenar por score
        alternatives.sort(key=lambda a: a.score, reverse=True)
        return alternatives[:5]

    def build_explanation(self, decision: Decision, problem: Problem) -> Explanation:
        reasons = []
        if decision.selected:
            reasons.append(f"Selecionado: {decision.selected.description}")
            reasons.extend(decision.selected.pros)
        if decision.hypotheses:
            reasons.append(decision.hypotheses[0].statement)

        rejected = []
        for alt in decision.alternatives:
            if decision.selected and alt.id != decision.selected.id:
                rejected.append(alt.description)

        return Explanation(
            summary=(
                decision.selected.description
                if decision.selected
                else "Não foi possível decidir com confiança suficiente"
            ),
            reasons=reasons,
            rejected=rejected[:3],
            assumptions=list(problem.assumptions),
            confidence=decision.confidence,
        )

    def build_plan(self, decision: Decision, goal: str) -> Plan:
        steps = [
            PlanStep(description="Interpretar o problema", order=0),
            PlanStep(description="Consultar contexto relevante", order=1),
            PlanStep(description="Avaliar alternativas", order=2),
            PlanStep(
                description=decision.selected.description if decision.selected else "Decidir",
                order=3,
            ),
        ]
        if decision.selected and decision.selected.risk in {RiskLevel.HIGH, RiskLevel.CRITICAL}:
            steps.append(
                PlanStep(
                    description="Solicitar autorização",
                    order=4,
                    requires_authorization=True,
                )
            )
        return Plan(goal=goal, steps=steps, confidence=decision.confidence)

    def propose_action(self, decision: Decision) -> ActionProposal | None:
        if not decision.selected:
            return None
        if decision.selected.risk in {RiskLevel.NONE, RiskLevel.LOW}:
            return None
        return ActionProposal(
            description=decision.selected.description,
            action_type="proposed",
            requires_authorization=True,
            risk=decision.selected.risk.value,
            confidence=decision.confidence,
        )
