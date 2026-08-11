"""Constantes do Knowledge System."""

from enum import Enum


class KnowledgeType(str, Enum):
    FACT = "fact"
    CONCEPT = "concept"
    ENTITY = "entity"
    RELATION = "relation"
    ASSERTION = "assertion"
    RULE = "rule"


class KnowledgeStatus(str, Enum):
    ACTIVE = "active"
    DISPUTED = "disputed"
    DEPRECATED = "deprecated"
    INVALIDATED = "invalidated"


class RelationType(str, Enum):
    IS_A = "is_a"
    PART_OF = "part_of"
    RELATED_TO = "related_to"
    CAUSES = "causes"
    DEPENDS_ON = "depends_on"
    SAME_AS = "same_as"
    OPPOSITE_OF = "opposite_of"
    CUSTOM = "custom"


DEFAULT_CONFIDENCE = 0.7
DEFAULT_MAX_RETRIEVAL = 20
