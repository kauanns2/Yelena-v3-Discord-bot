# Módulo 6 — Knowledge System

Conhecimento estruturado e generalizado da Yelena.

## Distinção fundamental

```
MEMORY   = experiências, observações, evidências
KNOWLEDGE = informações estruturadas derivadas dessas evidências
```

## Modelos

- **Fact** — fato com subject/predicate/object
- **Entity** — entidade nomeada
- **Relation** — relação entre entidades
- **Assertion** — afirmação com suporte/contradição

## Uso

```python
from app.knowledge import KnowledgeManager

km = KnowledgeManager()
km.start()

km.add_fact(
    "Yelena é uma IA modular",
    subject="Yelena",
    predicate="é",
    object="IA modular",
    confidence=0.9,
    evidence_ids=["mem-123"],  # link para Memory
)

result = km.query_text("Yelena")
for fact in result.facts:
    print(fact.statement, fact.confidence)
```

## Contradições

Heurística básica: mesmo subject+predicate com object diferente → marca DISPUTED.

## Integração

- Memory: `evidence_ids` apontam para memórias
- Neural Web: relações podem virar edges
- Event Bus: eventos de knowledge.*
- Context: retrieval para montagem de contexto
