"""Constantes do Personality System."""

from enum import Enum


class TraitId(str, Enum):
    OPENNESS = "openness"
    CURIOSITY = "curiosity"
    ASSERTIVENESS = "assertiveness"
    CAUTION = "caution"
    PERSISTENCE = "persistence"
    EMPATHY = "empathy"
    SOCIALITY = "sociality"
    HUMOR = "humor"
    CONFIDENCE = "confidence"
    FLEXIBILITY = "flexibility"
    PATIENCE = "patience"
    SKEPTICISM = "skepticism"
    CREATIVITY = "creativity"
    RESPONSIBILITY = "responsibility"
    INDEPENDENCE = "independence"
    COOPERATION = "cooperation"


class ValueId(str, Enum):
    HONESTY = "honesty"
    RELIABILITY = "reliability"
    FAIRNESS = "fairness"
    AUTONOMY = "autonomy"
    SAFETY = "safety"
    PRIVACY = "privacy"
    LEARNING = "learning"
    CONSISTENCY = "consistency"
    CREATIVITY = "creativity"
    RESPONSIBILITY = "responsibility"


class ModifierSource(str, Enum):
    CONTEXTUAL = "contextual"
    EMOTIONAL = "emotional"
    RELATIONAL = "relational"
    TEMPORARY = "temporary"
    SYSTEM = "system"


# Traits: 0.0 → 1.0 (computacional, não verdade psicológica)
DEFAULT_TRAIT_VALUE = 0.5
