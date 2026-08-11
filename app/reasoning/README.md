# Módulo 10 — Reasoning & Decision System

Produz **decisões estruturadas**. Não gera a resposta final em linguagem natural.

## Separação

```
Reasoning  → decide o que fazer / concluir
Language   → como dizer
Action     → executar (com autorização)
```

## Fluxo

```
Problem
  → Context / Memory / Knowledge
  → Personality + Emotion influence
  → Hypotheses + Alternatives
  → Evaluation
  → Decision + Explanation + Plan
  → (opcional) ActionProposal
```

## Uso

```python
from app.reasoning import ReasoningManager

rm = ReasoningManager()
rm.start()

decision = rm.analyze(
    "O usuário está preocupado com o projeto e pediu análise de riscos",
    context_items=["projeto Yelena", "preocupação recente"],
    personality_summary={"traits": {"caution": 0.6, "assertiveness": 0.55}},
    emotion_summary={"stress": 0.2, "valence": 0.1},
)

print(decision.status, decision.confidence)
print(decision.selected.description if decision.selected else None)
print(decision.metadata.get("explanation"))
```

## Princípios

- Pensar ≠ Executar
- Pode discordar / apontar riscos
- Pode pedir mais informação
- Segurança e autorização ficam fora deste módulo
