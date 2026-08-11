"""Testes do Emotion Manager."""

from app.emotion import EmotionManager
from app.emotion.constants import StimulusType, EmotionLabel


def test_baseline():
    em = EmotionManager()
    em.start()
    state = em.get_state()
    assert state.primary_emotion
    assert -1.0 <= state.valence <= 1.0


def test_positive_stimulus():
    em = EmotionManager()
    em.start()
    before = em.state.valence
    em.process_stimulus(intensity=0.8, valence=0.7, stimulus_type=StimulusType.USER)
    assert em.state.valence >= before


def test_negative_stimulus():
    em = EmotionManager()
    em.start()
    em.process_stimulus(intensity=0.8, valence=-0.7, stimulus_type=StimulusType.USER)
    assert em.state.valence < 0.3


def test_decay():
    em = EmotionManager()
    em.start()
    em.process_stimulus(intensity=0.9, valence=0.8)
    intensity_before = em.state.intensity
    em.tick(dt_seconds=600)
    assert em.state.intensity <= intensity_before


def test_summary():
    em = EmotionManager()
    em.start()
    summary = em.get_summary()
    assert "primary" in summary
    assert "valence" in summary


def test_reset():
    em = EmotionManager()
    em.start()
    em.process_stimulus(intensity=0.9, valence=-0.9)
    em.reset_to_baseline()
    assert em.state.source == "baseline"
