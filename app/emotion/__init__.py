"""
Módulo 8 — Emotion & Affective State System

Estados afetivos computacionais da Yelena.
Não afirma emoções humanas reais.
Não é Personality. Não é Memory.
"""

from app.emotion.manager import EmotionManager
from app.emotion.models.state import AffectiveState
from app.emotion.errors import EmotionError

__all__ = ["EmotionManager", "AffectiveState", "EmotionError"]
