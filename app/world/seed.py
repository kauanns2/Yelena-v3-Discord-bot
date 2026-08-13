"""Semear lore do mundo no Knowledge."""

from __future__ import annotations

import logging
from typing import Any

from app.world.lore import YELENA_HISTORY_FACTS

logger = logging.getLogger(__name__)


def seed_world_into_knowledge(knowledge: Any) -> None:
    if knowledge is None:
        return
    try:
        if hasattr(knowledge, "query_text"):
            existing = knowledge.query_text("Yelena vive no Brasil há cerca de 20 anos", limit=2)
            facts = getattr(existing, "facts", None) or getattr(existing, "items", None) or []
            if facts:
                logger.info("world seed skipped (already present)")
                return

        for text in YELENA_HISTORY_FACTS:
            knowledge.add_fact(
                text,
                confidence=0.95,
                source="world_seed",
                check_contradictions=False,
                metadata={"origin": "world"},
            )
        logger.info("world lore seeded into knowledge")
    except Exception:
        logger.exception("world seed failed")
