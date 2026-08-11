"""
Módulo 10 — Reasoning & Decision System

Transforma contexto, conhecimento, memória, personalidade e estado afetivo
em análises, hipóteses, planos e decisões estruturadas.

NÃO é o sistema de linguagem. NÃO escreve a resposta final.
"""

from app.reasoning.manager import ReasoningManager
from app.reasoning.models.decision import Decision
from app.reasoning.errors import ReasoningError

__all__ = ["ReasoningManager", "Decision", "ReasoningError"]
