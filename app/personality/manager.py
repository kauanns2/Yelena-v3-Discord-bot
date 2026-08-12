"""Personality Manager."""

from __future__ import annotations

import logging
import time
from typing import Any

from app.personality.constants import TraitId, ModifierSource
from app.personality.defaults import (
    default_yelena_profile,
    default_communication_style,
    default_social_style,
)
from app.personality.effective import compute_effective_traits
from app.personality.errors import PersonalityError, TraitError
from app.personality.models.profile import PersonalityProfile, PersonalityModifier, Trait
from app.personality.models.style import CommunicationStyle, SocialStyle

logger = logging.getLogger(__name__)


class PersonalityManager:
    """Gerencia o perfil de personalidade da Yelena.

    Personalidade influencia comportamento, não segurança.
    """

    def __init__(self, profile: PersonalityProfile | None = None) -> None:
        self._profile = profile or default_yelena_profile()
        self._communication = default_communication_style()
        self._social = default_social_style()
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
        logger.info(
            "personality system started",
            extra={"personality_name": self._profile.name},
        )

    def stop(self) -> None:
        self._started = False

    def get_summary(self) -> dict[str, Any]:
        self._metrics["reads"] += 1
        effective = compute_effective_traits(self._profile)
        return {
            "name": self._profile.name,
            "version": self._profile.version,
            "traits": effective,
            "values": dict(self._profile.values),
            "preferences": list(self._profile.preferences),
            "boundaries": list(self._profile.boundaries),
            "communication": self._communication.to_dict(),
            "social": self._social.to_dict(),
            "active_modifiers": len([m for m in self._profile.modifiers if not m.is_expired]),
        }

    def get_trait(self, trait_id: str | TraitId) -> float:
        key = trait_id.value if isinstance(trait_id, TraitId) else trait_id
        if key not in self._profile.traits:
            raise TraitError(f"Unknown trait: {key}", context={"trait": key})
        effective = compute_effective_traits(self._profile)
        return effective.get(key, self._profile.traits[key].value)

    def get_communication_style(self) -> dict[str, Any]:
        return self._communication.to_dict()

    def get_boundaries(self) -> list[str]:
        return list(self._profile.boundaries)

    def add_modifier(
        self,
        trait_id: str | TraitId,
        delta: float,
        *,
        source: ModifierSource = ModifierSource.TEMPORARY,
        duration: float | None = 3600.0,
        ttl: float | None = None,
        reason: str = "",
        context: str = "",
    ) -> PersonalityModifier:
        key = trait_id.value if isinstance(trait_id, TraitId) else trait_id
        if key not in self._profile.traits:
            raise TraitError(f"Unknown trait: {key}", context={"trait": key})

        dur = duration if duration is not None else ttl
        modifier = PersonalityModifier(
            trait_id=key,
            delta=max(-0.3, min(0.3, delta)),
            source=source,
            duration=dur,
            context=context or reason,
        )
        self._profile.modifiers.append(modifier)
        compute_effective_traits(self._profile)
        self._metrics["modifiers_added"] += 1
        return modifier

    def apply_emotion_influence(
        self,
        valence: float = 0.0,
        arousal: float = 0.0,
        *,
        duration: float = 300.0,
    ) -> None:
        """Influência temporária da emoção sobre traços (não altera baseline)."""
        # valência negativa + arousal → um pouco mais de cautela
        if valence < -0.2:
            self.add_modifier(
                TraitId.CAUTION,
                delta=min(0.15, abs(valence) * 0.15 + max(0.0, arousal) * 0.05),
                source=ModifierSource.EMOTIONAL,
                duration=duration,
                context="emotion_influence",
            )
        if valence > 0.3:
            self.add_modifier(
                TraitId.CONFIDENCE,
                delta=min(0.1, valence * 0.1),
                source=ModifierSource.EMOTIONAL,
                duration=duration,
                context="emotion_influence",
            )

    def update_trait(
        self,
        trait_id: str | TraitId,
        delta: float,
        *,
        source: ModifierSource = ModifierSource.SYSTEM,
    ) -> None:
        """Mudança gradual no baseline (limitada)."""
        key = trait_id.value if isinstance(trait_id, TraitId) else trait_id
        trait = self._profile.traits.get(key)
        if trait is None:
            raise TraitError(f"Unknown trait: {key}", context={"trait": key})

        capped = max(-0.05, min(0.05, delta))
        trait.baseline = max(trait.min_value, min(trait.max_value, trait.baseline + capped))
        compute_effective_traits(self._profile)
        self._profile.version += 1
        self._profile.updated_at = time.time()
        self._metrics["trait_updates"] += 1
        logger.info(
            "trait baseline updated",
            extra={"trait": key, "delta": delta, "source": source.value},
        )

    def health(self) -> dict[str, Any]:
        active = len([m for m in self._profile.modifiers if not m.is_expired])
        return {
            "status": "healthy" if self._started else "stopped",
            "name": self._profile.name,
            "traits": len(self._profile.traits),
            "active_modifiers": active,
            "metrics": dict(self._metrics),
        }
