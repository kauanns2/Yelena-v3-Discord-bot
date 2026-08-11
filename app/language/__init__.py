"""
Módulo 12 — Language & Response Generation System

Transforma ResponseSpecification em texto linguístico estruturado.
Não depende de um único provedor de IA.
"""

from app.language.manager import LanguageManager
from app.language.models.generation import GenerationResult
from app.language.errors import LanguageError

__all__ = ["LanguageManager", "GenerationResult", "LanguageError"]
