# Módulo 15 — Observability, Monitoring & Diagnostics

Sinais estruturados sobre o que acontece dentro da Yelena.

## O que é / o que não é

| É | Não é |
|---|--------|
| Métricas, logs, traces, health | Memory |
| Diagnóstico com evidência | Security Audit |
| Alertas | Reasoning / decisão autônoma |

## Uso

```python
from app.observability import ObservabilityManager

obs = ObservabilityManager()
obs.start()

obs.register_health("core", lambda: {"status": "healthy"})
obs.metrics.incr("requests_total")
obs.log("pipeline completed", module="runtime", correlation_id="abc")

report = obs.diagnose()
print(report.summary)
```

## Componentes

- StructuredLogger + redação de secrets
- MetricsRegistry (counter/gauge)
- Tracer (spans leves)
- HealthAggregator
- AlertManager (cooldown/dedup)
- DiagnosticsEngine

## Integração

Módulos registram health checkers.
Observability **não** chama Reasoning para decidir sozinha.
