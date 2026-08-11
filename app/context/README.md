# Módulo 7 — Cognitive Context System

Camada intermediária que organiza o contexto cognitivo para Reasoning, Conversation e Personality.

## O que é / o que não é

| É | Não é |
|---|--------|
| Contexto temporário da situação | Memory permanente |
| Seleção e compressão | Knowledge base |
| Budget de tokens | Reasoning |

## Fluxo

```
Situation
  → Memory retrieval
  → Knowledge retrieval
  → Neural relations (opcional)
  → Ranking + Dedup
  → Token budget
  → CognitiveContext
```

## Uso

```python
from app.context import ContextManager
from app.memory import MemoryManager
from app.knowledge import KnowledgeManager

memory = MemoryManager()
knowledge = KnowledgeManager()
ctx = ContextManager(memory_manager=memory, knowledge_manager=knowledge)
ctx.start()

context = ctx.build_from_text(
    "usuário preocupado com o projeto",
    session_id="s1",
    user_id="u1",
)

for item in context.items:
    print(item.source, item.relevance, item.content[:80])
```

## Budget

Controla quantos tokens/itens sobem para o próximo estágio.
Mensagens simples → contexto leve.
Situações complexas → mais itens, ainda dentro do budget.

## Integração

- Memory / Knowledge / Neural via adapters
- Reasoning e Conversation consomem `CognitiveContext`
- Event Bus: eventos `context.built` (futuro)
