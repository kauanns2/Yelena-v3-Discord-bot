"""
Camada de identidade narrativa da Yelena.

Não substitui Personality (traços) nem Emotion (estado).
Fornece brief estável + relações (Kauã, PH) para Language/Context/Knowledge.
"""

from app.identity.brief.builder import build_identity_brief
from app.identity.relations.canon import CANONICAL_RELATIONS, get_relation
from app.identity.seed import seed_identity_into_knowledge

__all__ = [
    "build_identity_brief",
    "CANONICAL_RELATIONS",
    "get_relation",
    "seed_identity_into_knowledge",
]
