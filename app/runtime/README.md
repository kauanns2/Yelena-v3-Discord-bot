# Módulo 16 — Runtime & Orchestration

Camada que conecta todos os módulos em um runtime coerente.

## Princípio

```
Runtime coordena
Módulos executam sua responsabilidade
```

Não é God Object.

## Ativação seletiva

| Complexidade | Módulos típicos |
|--------------|-----------------|
| trivial (oi) | conversation, language, emotion leve |
| simple | + personality, memory residual |
| normal | + context, reasoning |
| complex | pipeline completo |
| critical | + security gate |

## Uso

```python
from app.runtime import YelenaRuntime

rt = YelenaRuntime()
rt.start()

response = rt.process("oi", user_id="kauanns2")
print(response.text)
print(response.modules_used)

rt.stop()
```

## Lifecycle

```
CREATED → STARTING → READY ⇄ DEGRADED → STOPPING → STOPPED
```

## Arquitetura final

```
        RUNTIME
           │
  Config · Security · Observability
           │
       Event Bus / Neural Web
           │
 Memory · Knowledge · Context · Emotion · Personality
           │
       Reasoning
           │
     Conversation → Language
           │
         Action
```
