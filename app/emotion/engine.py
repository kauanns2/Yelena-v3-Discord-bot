"""Motor de transição afetiva."""

from __future__ import annotations

import time

from app.emotion.constants import EmotionLabel, DEFAULT_DECAY_RATE
from app.emotion.models.state import AffectiveState, EmotionVector
from app.emotion.models.stimulus import Stimulus
from app.emotion.models.transition import Transition


class EmotionEngine:
    """Aplica estímulos, decay e recovery sobre o estado afetivo.

    Regras são computacionais e configuráveis — não psicologia humana real.
    """

    def __init__(
        self,
        decay_rate: float = DEFAULT_DECAY_RATE,
        recovery_rate: float = 0.02,
    ) -> None:
        self.decay_rate = decay_rate
        self.recovery_rate = recovery_rate

    def apply_stimulus(self, state: AffectiveState, stimulus: Stimulus) -> Transition:
        from_primary = state.primary_emotion
        from_valence = state.valence

        # influência do estímulo (política simples e configurável depois)
        influence = stimulus.intensity * (0.3 + 0.7 * (1.0 - state.stability))

        state.valence = _clamp(state.valence + stimulus.valence * influence, -1.0, 1.0)
        state.arousal = _clamp01(state.arousal + abs(stimulus.valence) * influence * 0.5)
        state.intensity = _clamp01(max(state.intensity, stimulus.intensity * 0.8))

        # atualizar vetor emocional de forma heurística
        label = self._infer_label(state.valence, state.arousal)
        state.vector.set(label, max(state.vector.get(label), stimulus.intensity))
        state.sync_primary_from_vector()

        state.triggers.append(stimulus.id)
        state.source = stimulus.source or stimulus.stimulus_type.value
        state.updated_at = time.time()
        state.version += 1

        magnitude = abs(state.valence - from_valence) + abs(
            (1 if state.primary_emotion != from_primary else 0)
        )

        return Transition(
            from_primary=from_primary,
            to_primary=state.primary_emotion,
            from_valence=from_valence,
            to_valence=state.valence,
            magnitude=magnitude,
            stimulus_id=stimulus.id,
            cause="stimulus",
            correlation_id=stimulus.correlation_id,
        )

    def decay(self, state: AffectiveState, dt_seconds: float = 1.0) -> AffectiveState:
        factor = max(0.0, 1.0 - self.decay_rate * (dt_seconds / 60.0))
        # intensidade e arousal decaem em direção ao baseline baixo
        state.intensity *= factor
        state.arousal = state.arousal * factor + DEFAULT_AROUSAL_TARGET * (1 - factor)

        # valence tende lentamente ao baseline 0
        state.valence *= factor

        # vetor decai
        for k in list(state.vector.weights.keys()):
            state.vector.weights[k] *= factor
            if state.vector.weights[k] < 0.05:
                del state.vector.weights[k]

        state.sync_primary_from_vector()
        if not state.vector.weights:
            state.primary_emotion = EmotionLabel.NEUTRAL.value
            state.intensity = min(state.intensity, 0.2)

        state.updated_at = time.time()
        return state

    def recover(self, state: AffectiveState, dt_seconds: float = 1.0) -> AffectiveState:
        """Recuperação em direção ao baseline."""
        t = min(1.0, self.recovery_rate * (dt_seconds / 60.0))
        state.stress = _clamp01(state.stress * (1 - t))
        state.fatigue = _clamp01(state.fatigue * (1 - t * 0.5))
        state.energy = _clamp01(state.energy + t * 0.1)
        state.stability = _clamp01(state.stability + t * 0.05)
        state.updated_at = time.time()
        return state

    def _infer_label(self, valence: float, arousal: float) -> str:
        if valence >= 0.3 and arousal >= 0.5:
            return EmotionLabel.EXCITED.value if arousal > 0.7 else EmotionLabel.HAPPY.value
        if valence >= 0.3 and arousal < 0.5:
            return EmotionLabel.CONTENT.value if valence < 0.6 else EmotionLabel.CALM.value
        if valence <= -0.3 and arousal >= 0.5:
            return EmotionLabel.ANGRY.value if arousal > 0.7 else EmotionLabel.FRUSTRATED.value
        if valence <= -0.3 and arousal < 0.5:
            return EmotionLabel.SAD.value if valence < -0.5 else EmotionLabel.DISTANT.value
        if arousal >= 0.6:
            return EmotionLabel.CURIOUS.value
        return EmotionLabel.NEUTRAL.value


DEFAULT_AROUSAL_TARGET = 0.3


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def _clamp01(v: float) -> float:
    return max(0.0, min(1.0, v))
