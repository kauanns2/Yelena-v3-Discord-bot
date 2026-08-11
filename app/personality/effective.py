"""Cálculo de personalidade efetiva (baseline + modifiers)."""

from __future__ import annotations

import time

from app.personality.models.profile import PersonalityProfile, Trait


def compute_effective_traits(profile: PersonalityProfile) -> dict[str, float]:
    """baseline + modifiers ativos, respeitando min/max."""
    # limpar expirados
    profile.modifiers = [m for m in profile.modifiers if not m.is_expired]

    effective: dict[str, float] = {}
    for trait_id, trait in profile.traits.items():
        value = trait.baseline
        for mod in profile.modifiers:
            if mod.trait_id == trait_id:
                value += mod.delta
        value = max(trait.min_value, min(trait.max_value, value))
        effective[trait_id] = value
        # value atual reflete effective (baseline permanece)
        trait.value = value
        trait.updated_at = time.time()

    return effective
