"""Constantes do Emotion System."""

from enum import Enum


class EmotionLabel(str, Enum):
    CALM = "calm"
    CONTENT = "content"
    HAPPY = "happy"
    EXCITED = "excited"
    CURIOUS = "curious"
    INTERESTED = "interested"
    CONFIDENT = "confident"
    UNCERTAIN = "uncertain"
    SAD = "sad"
    FRUSTRATED = "frustrated"
    ANGRY = "angry"
    ANXIOUS = "anxious"
    STRESSED = "stressed"
    FEARFUL = "fearful"
    SURPRISED = "surprised"
    BORED = "bored"
    TIRED = "tired"
    RELIEVED = "relieved"
    ATTACHED = "attached"
    DISTANT = "distant"
    NEUTRAL = "neutral"


class StimulusType(str, Enum):
    CONVERSATION = "conversation"
    MEMORY = "memory"
    KNOWLEDGE = "knowledge"
    SYSTEM = "system"
    USER = "user"
    EVENT = "event"
    INTERNAL = "internal"
    EXTERNAL = "external"


# Escalas documentadas:
# valence: -1.0 → +1.0
# arousal, dominance, intensity, stability, confidence: 0.0 → 1.0

DEFAULT_VALENCE = 0.0
DEFAULT_AROUSAL = 0.3
DEFAULT_DOMINANCE = 0.5
DEFAULT_INTENSITY = 0.3
DEFAULT_STABILITY = 0.7
DEFAULT_DECAY_RATE = 0.05
