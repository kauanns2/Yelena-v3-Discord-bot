# Módulo 9 — Personality & Behavioral Identity

Identidade comportamental **relativamente estável** da Yelena.

## Separação

| Sistema | Papel |
|---------|--------|
| Personality | Tendências estáveis, valores, estilo |
| Emotion | Estado afetivo dinâmico |
| Memory | Experiências |

## Conceitos

- **Traits** — 0.0→1.0 (curiosity, empathy, assertiveness…)
- **Baseline** — valor estável do trait
- **Modifiers** — ajustes temporários (contexto, emoção, relação)
- **Effective** — baseline + modifiers (sem sobrescrever baseline)
- **Values** — prioridades (honesty, safety, privacy…)
- **Boundaries** — limites comportamentais
- **Communication / Social style**

## Uso

```python
from app.personality import PersonalityManager
from app.personality.constants import TraitId

pm = PersonalityManager()
pm.start()

print(pm.get_trait(TraitId.CURIOSITY))
print(pm.get_summary())

# modifier temporário (não altera baseline)
pm.add_modifier(TraitId.CAUTION, 0.1, duration=60, context="situação de risco")
```

## Regra importante

Uma interação **não** deve fazer:

```
insulto → aggressiveness permanentemente +0.5
```

Mudança permanente exige política de evolução + evidência + validação (futuro).

## Integração

- Emotion → modifiers temporários via `apply_emotion_influence`
- Context / Reasoning / Language consomem `get_summary()`
