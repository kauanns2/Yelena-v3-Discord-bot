# Módulo 1 — Core & Kernel

Fundação operacional da Yelena V3.

## Propósito

O Core fornece infraestrutura para todos os outros módulos:

- Lifecycle (ciclo de vida)
- Registry (registro de módulos)
- Dependency resolution (grafo + ciclos)
- State (estado global tipado)
- Health checks
- Loader
- Shutdown ordenado
- Contratos / protocols

**O Core não implementa:** personalidade, memória, emoção, Discord, IA, voz ou raciocínio.

## Princípio

> O Core conhece contratos, não detalhes de implementação.

## Componentes

| Arquivo | Responsabilidade |
|---------|------------------|
| `bootstrap.py` | Preparação inicial |
| `kernel.py` | Coordenador central |
| `lifecycle.py` | Estados e transições |
| `registry.py` | Registro de módulos |
| `dependency.py` | Grafo e ordem de init/shutdown |
| `loader.py` | Carregamento de módulos |
| `state.py` | Estado global |
| `health.py` | Health checks |
| `shutdown.py` | Encerramento seguro |
| `protocols.py` | Contratos |
| `exceptions.py` | Hierarquia de erros |

## Lifecycle

```
CREATED → BOOTSTRAPPING → STARTING → RUNNING
                                    ↘ DEGRADED
                         STOPPING → STOPPED
                         FAILED
```

## Uso básico

```python
from app.core.bootstrap import Bootstrap

bootstrap = Bootstrap(environment="development")
bootstrap.prepare()

kernel = bootstrap.create_kernel()
await kernel.start()

print(kernel.status())

await kernel.stop()
```

## Integração futura

O Core está preparado para:

- Configuration (Módulo 2)
- Neural Web (Módulo 3)
- Event Bus (Módulo 4)
- e os demais 12 módulos

via contratos, registry e lifecycle — sem acoplamento direto.

## Decisões arquiteturais

1. Sem God Object — Kernel só coordena
2. Sem lógica de domínio no Core
3. Dependências explícitas com detecção de ciclos
4. Shutdown na ordem inversa das dependências
5. Health agregável e extensível
6. Estado tipado, não dict global arbitrário
