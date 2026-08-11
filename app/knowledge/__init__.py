"""
Módulo 6 — Knowledge System

Conhecimento estruturado e generalizado derivado de evidências.
Não é Memory (experiências). Não é Context (situação atual).
"""

from app.knowledge.manager import KnowledgeManager
from app.knowledge.models.fact import Fact
from app.knowledge.errors import KnowledgeError

__all__ = ["KnowledgeManager", "Fact", "KnowledgeError"]
