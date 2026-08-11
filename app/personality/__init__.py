"""
Módulo 9 — Personality & Behavioral Identity System

Identidade comportamental relativamente estável da Yelena.
Não é Emotion (dinâmico). Não é Memory. Não é um prompt gigante.
"""

from app.personality.manager import PersonalityManager
from app.personality.models.profile import PersonalityProfile
from app.personality.errors import PersonalityError

__all__ = ["PersonalityManager", "PersonalityProfile", "PersonalityError"]
