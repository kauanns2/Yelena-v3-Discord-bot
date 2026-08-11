# Módulo 8 — Emotion & Affective State System

Estados afetivos **computacionais** da Yelena.

> Não afirma que esses estados são emoções humanas reais.

## Separação

| Sistema | Papel |
|---------|--------|
| Emotion | Estado afetivo dinâmico |
| Personality | Tendências estáveis |
| Memory | Experiências |

## Dimensões

- **Valence** −1.0 → +1.0
- **Arousal / Dominance / Intensity / Stability** 0.0 → 1.0
- **Emotion Vector** — mistura de labels

## Fluxo

```
Stimulus → Interpretation hooks → Affective response → Transition → Decay/Recovery → Current State
```

## Uso

```python
from app.emotion import EmotionManager
from app.emotion.constants import StimulusType

em = EmotionManager()
em.start()

em.process_stimulus(
    intensity=0.6,
    valence=0.4,
    stimulus_type=StimulusType.CONVERSATION,
    source="user",
)

print(em.get_summary())
em.tick(dt_seconds=60)
```

## PH / Internal state

`energy`, `fatigue`, `stress`, `ph` são sinais internos.
A influência do PH sobre emoção é política configurável futura — não hardcoded.

## Integração

- Context: `get_summary()`
- Memory: eventos emocionais importantes (via Event Bus)
- Personality: modifiers temporários (Módulo 9)
