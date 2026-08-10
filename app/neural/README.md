# Módulo 3 — Neural Web / Teia Neural

Infraestrutura de relacionamento e propagação de sinais entre componentes da Yelena.

## O que é

A Teia representa **como as partes se conectam**, não a lógica de cada parte.

```
Core → Configuration → Neural Web → conecta módulos
```

## O que NÃO é

- Não é Event Bus (isso é o Módulo 4)
- Não é Memory / Knowledge / Emotion
- Não é God Object

## Componentes

| Componente | Função |
|------------|--------|
| `Node` | Ponto na teia (módulo, serviço, entidade) |
| `Edge` | Relação entre nós |
| `Signal` | Informação que viaja pela teia |
| `Topology` | Grafo de conexões |
| `Propagator` | Entrega sinais com TTL e anti-loop |
| `Manager` | Coordenação |

## Proteções

- **TTL** — sinal expira
- **Max hops** — profundidade limitada
- **Loop detection** — path tracking
- **Active nodes only** — não entrega em nós inativos

## Uso

```python
from app.neural import NeuralWebManager, Signal
from app.neural.constants import NodeType, SignalType

web = NeuralWebManager()
web.register_node("memory", NodeType.MODULE)
web.register_node("emotion", NodeType.MODULE)
web.connect("memory", "emotion")

web.on_signal("emotion", lambda sig, nid: print(sig.payload))

signal = Signal(
    signal_type=SignalType.EVENT,
    source_id="memory",
    payload={"event": "memory.recalled"},
)
web.emit(signal)
```

## Integração

- Core: lifecycle + health
- Configuration: max_hops, ttl, queue size
- Event Bus (Módulo 4): sinais podem virar eventos formais
