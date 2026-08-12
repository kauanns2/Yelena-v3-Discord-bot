# Yelena V3 — Estrutura e Teia Neural

Documento mestre. Catálogo detalhado: [MODULES.md](./MODULES.md).

## Convenção de pastas

```text
módulo/
  README.md
  manager.py       # fachada
  models/          # dados
  <submódulo>/     # grupo claro
```

## Camadas

```text
EDGE
  bridge/ (17)   integration/

ORQUESTRAÇÃO
  runtime/ (16)  core/ (1)  configuration/ (2)

SINAIS
  neural/ (3)    event_bus/ (4)

COGNIÇÃO / IDENTIDADE
  memory (5) knowledge (6) context (7)
  emotion (8) personality (9) identity/
  reasoning (10)

EXPRESSÃO / AÇÃO
  conversation (11) language (12) actions (13)
  voice/ (futuro)

PROTEÇÃO / OBSERVAÇÃO
  security (14) observability (15)
```

## Teia Neural

A Teia **não** é o pipeline.  
Pipeline = ordem do turno.  
Teia = mapa de relações + propagação de sinais entre módulos.

No boot, o Runtime registra nós e arestas canônicas (ver `runtime._wire_neural_topology`).

## Regras ao editar

1. Entrar pelo `manager.py` do módulo.
2. Discord só em `bridge/platforms/`.
3. Secrets só via Configuration / env.
4. Persona narrativa em `identity/` + Knowledge seed.
5. Evolução: `bridge/evolution` registra; Personality aplica delta limitado.
6. Voice não redefine persona — só sintetiza texto.

## Futuro permitido

```text
app/voice/           # TTS
app/relationship/    # grafo de vínculos rico
app/world/           # lore expandido
```

Adicionar só com responsabilidade clara.
