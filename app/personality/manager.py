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
from app.personality.errors import TraitError, ModifierError
from app.personality.models.profile import PersonalityProfile, Trait, PersonalityModifier
from app.personality.models.style import CommunicationStyle, SocialStyle

logger = logging.getLogger(__name__)


class PersonalityManager:
    """Gerencia identidade comportamental estável da Yelena.

    Modifiers temporários não alteram o baseline permanentemente.
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
        logger.info("personality system started", extra={"name": self._profile.name})

    def stop(self) -> None:
        self._started = False

    def get_effective_traits(self) -> dict[str, float]:
        self._metrics["reads"] += 1
        return compute_effective_traits(self._profile)

    def get_trait(self, trait_id: str | TraitId) -> float:
        key = trait_id.value if isinstance(trait_id, TraitId) else trait_id
        effective = self.get_effective_traits()
        if key not in effective:
            raise TraitError(f"Unknown trait: {key}", context={"trait_id": key})
        return effective[key]

    def get_summary(self) -> dict[str, Any]:
        """Resumo para Context / Reasoning / Language."""
        effective = self.get_effective_traits()
        return {
            "name": self._profile.name,
            "traits": effective,
            "top_traits": sorted(effective.items(), key=lambda x: x[1], reverse=True)[:6],
            "values": dict(self._profile.values),
            "preferences": list(self._profile.preferences),
            "boundaries": list(self._profile.boundaries),
            "communication": self._communication.to_dict(),
            "social": self._social.to_dict(),
        }

    def add_modifier(
        self,
        trait_id: str | TraitId,
        delta: float,
        *,
        source: ModifierSource = ModifierSource.TEMPORARY,
        duration: float | None = 300.0,
        context: str = "",
        confidence: float = 0.7,
    ) -> PersonalityModifier:
        key = trait_id.value if isinstance(trait_id, TraitId) else trait_id
        if key not in self._profile.traits:
            raise ModifierError(f"Cannot modify unknown trait: {key}")

        # limitar delta extremo
        delta = max(-0.3, min(0.3, delta))

        mod = PersonalityModifier(
            trait_id=key,
            delta=delta,
            source=source,
            duration=duration,
            context=context,
            confidence=confidence,
        )
        self._profile.modifiers.append(mod)
        self._metrics["modifiers_added"] += 1
        compute_effective_traits(self._profile)
        logger.debug(
            "modifier added",
            extra={"trait": key, "delta": delta, "source": source.value},
        )
        return mod

    def purge_expired_modifiers(self) -> int:
        before = len(self._profile.modifiers)
        self._profile.modifiers = [m for m in self._profile.modifiers if not m.is_expired]
        removed = before - len(self._profile.modifiers)
        self._metrics["modifiers_expired"] += removed
        if removed:
            compute_effective_traits(self._profile)
        return removed

    def apply_emotion_influence(self, valence: float, arousal: float) -> None:
        """Modifiers temporários leves a partir do estado afetivo — não muda baseline."""
        self.purge_expired_modifiers()
        if valence > 0.4:
            self.add_modifier(TraitId.SOCIALITY, 0.05, source=ModifierSource.EMOTIONAL, duration=120)
            self.add_modifier(TraitId.HUMOR, 0.05, source=ModifierSource.EMOTIONAL, duration=120)
        elif valence < -0.4:
            self.add_modifier(TraitId.CAUTION, 0.08, source=ModifierSource.EMOTIONAL, duration=120)
            self.add_modifier(TraitId.SOCIALITY, -0.05, source=ModifierSource.EMOTIONAL, duration=120)
        if arousal > 0.7:
            self.add_modifier(TraitId.CURIOSITY, 0.05, source=ModifierSource.EMOTIONAL, duration=90)

    def communication_style(self) -> CommunicationStyle:
        return self._communication

    def social_style(self) -> SocialStyle:
        return self._social

    def health(self) -> dict[str, Any]:
        return {
            "status": "healthy" if self._started else "stopped",
            "name": self._profile.name,
            "traits": len(self._profile.traits),
            "active_modifiers": len([m for m in self._profile.modifiers if not m.is_expired]),
            "metrics": dict(self._metrics),
        }
