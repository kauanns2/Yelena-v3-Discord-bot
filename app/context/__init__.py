"""
Módulo 7 — Cognitive Context System

Camada intermediária que monta o contexto cognitivo relevante
para Reasoning / Conversation / Personality.

Não é Memory. Não é Knowledge. Não é Reasoning.
"""

from app.context.manager import ContextManager
from app.context.models.context import CognitiveContext
from app.context.errors import ContextError

__all__ = ["ContextManager", "CognitiveContext", "ContextError"]
