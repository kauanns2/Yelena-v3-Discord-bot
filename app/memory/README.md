# Módulo 5 — Memory System

Sistema de memória da Yelena V3.

## Distinções

| Sistema | Função |
|---------|--------|
| **Memory** | Experiências, episódios, preferências, emoções associadas |
| Knowledge | Conhecimento estruturado e generalizado |
| Context | Estado cognitivo temporário da situação atual |

## Tipos de memória

- episodic, semantic, preference
- autobiographical, emotional, working
- procedural, relational, factual, contextual

## Ciclo de vida

```
create → active → (reinforce) → consolidated
                 → decaying → forgotten
                 → archived
```

## Uso

```python
from app.memory import MemoryManager
from app.memory.constants import MemoryType
from app.memory.models.query import MemoryQuery

mm = MemoryManager()
mm.start()

mem = mm.create(
    "Usuário está preocupado com o projeto",
    memory_type=MemoryType.EPISODIC,
    importance=0.8,
    tags=["projeto", "preocupação"],
)

result = mm.recall_text("projeto")
for m in result.memories:
    print(m.content, result.scores[m.id])
```

## Políticas

- **Decay** — força diminui com o tempo
- **Reinforce** — acesso/relevância aumentam força
- **Consolidate** — memórias importantes ficam mais estáveis
- **Forget** — memórias fracas/expiradas podem ser esquecidas

## Privacidade

Níveis: public → internal → private → sensitive → restricted

## Integração

- Event Bus: `memory.created`, `memory.recalled`, etc. (futuro)
- Neural Web: associações
- Configuration: TTL, limits, decay rates
