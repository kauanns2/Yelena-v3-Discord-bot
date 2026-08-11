"""Testes do Personality Manager."""

import pytest

from app.personality import PersonalityManager
from app.personality.constants import TraitId, ModifierSource
from app.personality.errors import TraitError


def test_default_profile():
    pm = PersonalityManager()
    pm.start()
    curiosity = pm.get_trait(TraitId.CURIOSITY)
    assert curiosity > 0.5


def test_summary():
    pm = PersonalityManager()
    pm.start()
    summary = pm.get_summary()
    assert summary["name"] == "Yelena"
    assert "traits" in summary
    assert "communication" in summary


def test_modifier_does_not_change_baseline():
    pm = PersonalityManager()
    pm.start()
    trait = pm.profile.traits[TraitId.CAUTION.value]
    baseline = trait.baseline
    pm.add_modifier(TraitId.CAUTION, 0.2, duration=60)
    assert trait.baseline == baseline
    assert pm.get_trait(TraitId.CAUTION) > baseline


def test_unknown_trait():
    pm = PersonalityManager()
    pm.start()
    with pytest.raises(TraitError):
        pm.get_trait("nonexistent_trait")


def test_emotion_influence():
    pm = PersonalityManager()
    pm.start()
    before = pm.get_trait(TraitId.CAUTION)
    pm.apply_emotion_influence(valence=-0.6, arousal=0.4)
    after = pm.get_trait(TraitId.CAUTION)
    assert after >= before
