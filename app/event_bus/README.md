# Módulo 4 — Event Bus

Comunicação formal baseada em eventos entre componentes da Yelena.

## Papéis

| Sistema | Função |
|---------|--------|
| Core | Lifecycle |
| Configuration | Config |
| Neural Web | Relações e sinais |
| **Event Bus** | Eventos formais |

## Princípio

```
Produtor → Event Bus → Subscribers
```

O produtor não conhece os consumidores.

## Uso

```python
from app.event_bus import EventBus

bus = EventBus()
bus.start()

def on_memory_recalled(event):
    print(event.payload)

bus.subscribe("memory.recalled", on_memory_recalled)

bus.publish(
    "memory.recalled",
    payload={"memory_id": "abc"},
    source="memory",
    correlation_id="req-123",
)
```

## Recursos

- Publish / Subscribe / Unsubscribe
- Filtros por nome, source, prioridade
- Wildcard (`module.*`)
- TTL e drop de eventos expirados
- Deduplicação básica
- Middleware pipeline
- Correlation / causation / trace IDs
- Métricas e health

## Integração

- Core: lifecycle
- Configuration: max_queue, ttl, retries
- Neural Web: sinais podem gerar eventos formais
