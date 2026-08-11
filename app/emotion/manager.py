"""Emotion Manager."""

from __future__ import annotations

import logging
import time
from typing import Any

from app.emotion.constants import EmotionLabel, StimulusType, DEFAULT_DECAY_RATE
from app.emotion.engine import EmotionEngine
from app.emotion.models.state import AffectiveState, EmotionVector
from app.emotion.models.stimulus import Stimulus
from app.emotion.models.transition import Transition

logger = logging.getLogger(__name__)


class EmotionManager:
    """Gerencia o estado afetivo atual da Yelena.

    Estados computacionais — não afirmações de emoção humana real.
    """

    def __init__(self, decay_rate: float = DEFAULT_DECAY_RATE) -> None:
        self._engine = EmotionEngine(decay_rate=decay_rate)
        self._state = self._baseline_state()
        self._history: list[Transition] = []
        self._max_history = 50
        self._started = False
        self._metrics = {
            "stimuli_received": 0,
            "transitions": 0,
            "decay_operations": 0,
            "recovery_operations": 0,
        }

    def _baseline_state(self) -> AffectiveState:
        vector = EmotionVector()
        vector.set(EmotionLabel.CALM, 0.4)
        vector.set(EmotionLabel.NEUTRAL, 0.3)
        state = AffectiveState(
            primary_emotion=EmotionLabel.CALM.value,
            vector=vector,
            valence=0.1,
            arousal=0.25,
            intensity=0.25,
            stability=0.75,
            source="baseline",
        )
        state.sync_primary_from_vector()
        return state

    @property
    def is_started(self) -> bool:
        return self._started

    @property
    def state(self) -> AffectiveState:
        return self._state

    def start(self) -> None:
        self._started = True
        logger.info("emotion system started", extra={"primary": self._state.primary_emotion})

    def stop(self) -> None:
        self._started = False

    def get_state(self) -> AffectiveState:
        return self._state

    def get_summary(self) -> dict[str, Any]:
        """Resumo para Cognitive Context — não o histórico inteiro."""
        s = self._state
        return {
            "primary": s.primary_emotion,
            "secondary": list(s.secondary_emotions),
            "valence": s.valence,
            "arousal": s.arousal,
            "intensity": s.intensity,
            "stability": s.stability,
            "confidence": s.confidence,
            "stress": s.stress,
            "energy": s.energy,
        }

    def process_stimulus(
        self,
        *,
        intensity: float = 0.5,
        valence: float = 0.0,
        stimulus_type: StimulusType = StimulusType.CONVERSATION,
        source: str = "",
        correlation_id: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> Transition:
        stimulus = Stimulus(
            stimulus_type=stimulus_type,
            source=source,
            intensity=intensity,
            valence=valence,
            correlation_id=correlation_id,
            context=context or {},
        )
        transition = self._engine.apply_stimulus(self._state, stimulus)
        self._history.append(transition)
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history :]
        self._metrics["stimuli_received"] += 1
        self._metrics["transitions"] += 1
        logger.debug(
            "stimulus processed",
            extra={
                "from": transition.from_primary,
                "to": transition.to_primary,
                "valence": self._state.valence,
            },
        )
        return transition

    def tick(self, dt_seconds: float = 1.0) -> None:
        """Decay + recovery periódicos."""
        self._engine.decay(self._state, dt_seconds)
        self._engine.recover(self._state, dt_seconds)
        self._metrics["decay_operations"] += 1
        self._metrics["recovery_operations"] += 1

    def reset_to_baseline(self) -> None:
        self._state = self._baseline_state()
        logger.info("emotion reset to baseline")

    def set_ph(self, ph: float) -> None:
        """Interface para PH — política de influência fica em módulos futuros."""
        self._state.ph = ph
        self._state.updated_at = time.time()

    def health(self) -> dict[str, Any]:
        return {
            "status": "healthy" if self._started else "stopped",
            "primary": self._state.primary_emotion,
            "valence": self._state.valence,
            "intensity": self._state.intensity,
            "metrics": dict(self._metrics),
        }
