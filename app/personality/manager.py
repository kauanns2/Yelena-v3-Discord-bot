"""Personality Manager."""

from __future__ import annotations

import logging
import time
from typing import Any

from app.personality.constants import TraitId, ModifierSource
from app.personality.defaults import create_default_yelena_profile
from app.personality.effective import compute_effective_traits
from app.personality.errors import PersonalityError
from app.personality.models.profile import PersonalityProfile, TraitModifier

logger = logging.getLogger(__name__)


class PersonalityManager:
    """Gerencia o perfil de personalidade da Yelena.

    Personalidade influencia comportamento, não segurança.
    """

    def __init__(self, profile: PersonalityProfile | None = None) -> None:
        self._profile = profile or create_default_yelena_profile()
        self._started = False
        self._metrics = {
            "reads": 0,
            "modifiers_added": 0,
            "modifiers_expired": 0,
            "trait_updates": 0,
        }

    @property
    def is_started(self) -> bool:
        return self._started

    @property
    def profile(self) -> PersonalityProfile:
        return self._profile

    def start(self) -> None:
        self._started = True
        compute_effective_traits(self._profile)
        logger.info("personality system started", extra={"personality_name": self._profile.name})

    def stop(self) -> None:
        self._started = False

    def get_summary(self) -> dict[str, Any]:
        self._metrics["reads"] += 1
        self._expire_modifiers()
        return self._profile.summary()

    def get_trait(self, trait_id: str | TraitId) -> float:
        self._expire_modifiers()
        key = trait_id.value if isinstance(trait_id, TraitId) else trait_id
        return self._profile.effective_traits.get(key, self._profile.traits.get(key, 0.5))

    def get_communication_style(self) -> dict[str, Any]:
        return self._profile.communication.to_dict()

    def get_boundaries(self) -> list[str]:
        return list(self._profile.boundaries)

    def add_modifier(
        self,
        trait_id: str | TraitId,
        delta: float,
        *,
        source: ModifierSource = ModifierSource.CONTEXT,
        ttl: float | None = 3600.0,
        reason: str = "",
    ) -> TraitModifier:
        key = trait_id.value if isinstance(trait_id, TraitId) else trait_id
        if key not in self._profile.traits:
            raise PersonalityError(f"Unknown trait: {key}", context={"trait": key})

        expires = time.time() + ttl if ttl else None
        modifier = TraitModifier(
            trait_id=key,
            delta=max(-0.3, min(0.3, delta)),
            source=source,
            expires_at=expires,
            reason=reason,
        )
        self._profile.modifiers.append(modifier)
        compute_effective_traits(self._profile)
        self._metrics["modifiers_added"] += 1
        return modifier

    def update_trait(
        self,
        trait_id: str | TraitId,
        delta: float,
        *,
        source: ModifierSource = ModifierSource.LEARNING,
    ) -> None:
        """Mudança gradual no baseline (limitada)."""
        key = trait_id.value if isinstance(trait_id, TraitId) else trait_id
        if key not in self._profile.traits:
            raise PersonalityError(f"Unknown trait: {key}")

        # mudanças de baseline muito pequenas
        capped = max(-0.05, min(0.05, delta))
        self._profile.traits[key] = max(0.0, min(1.0, self._profile.traits[key] + capped))
        compute_effective_traits(self._profile)
        self._profile.version += 1
        self._metrics["trait_updates"] += 1
        logger.info(
            "trait baseline updated",
            extra={"trait": key, "delta": delta, "source": source.value},
        )

    def _expire_modifiers(self) -> None:
        before = len(self._profile.modifiers)
        now = time.time()
        self._profile.modifiers = [
            m
            for m in self._profile.modifiers
            if m.expires_at is None or m.expires_at > now
        ]
        expired = before - len(self._profile.modifiers)
        if expired:
            self._metrics["modifiers_expired"] += expired
            compute_effective_traits(self._profile)

    def health(self) -> dict[str, Any]:
        return {
            "status": "healthy" if self._started else "stopped",
            "name": self._profile.name,
            "traits": len(self._profile.traits),
            "active_modifiers": len(self._profile.modifiers),
            "metrics": dict(self._metrics),
        }
