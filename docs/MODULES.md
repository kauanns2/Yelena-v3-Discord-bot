# Yelena V3 — Catálogo de módulos

Formato padrão de cada módulo:

```text
app/<módulo>/
├── README.md          # o que faz / o que NÃO faz
├── __init__.py        # exporta Manager + erros públicos
├── manager.py         # fachada (único ponto de entrada preferido)
├── constants.py
├── errors.py
├── types.py
├── models/            # dados (dataclasses)
│   └── ...
└── <submódulo>/       # só se o grupo for claro
    └── ...
```

**Regra:** ao mexer, entre pelo `manager.py`. Não importe miolo interno de outro módulo se o manager já expõe a função.

---

## Camadas (de fora para dentro)

```text
┌─────────────────────────────────────────────────────────┐
│ EDGE                                                    │
│   bridge/ (17)     integration/ (HTTP)                  │
├─────────────────────────────────────────────────────────┤
│ ORQUESTRAÇÃO                                            │
│   runtime/ (16)    core/ (1)    configuration/ (2)      │
├─────────────────────────────────────────────────────────┤
│ SINAIS                                                  │
│   neural/ (3)      event_bus/ (4)                       │
├─────────────────────────────────────────────────────────┤
│ COGNIÇÃO + IDENTIDADE                                   │
│   memory (5) knowledge (6) context (7)                  │
│   emotion (8) personality (9) identity (—)              │
│   reasoning (10)                                        │
├─────────────────────────────────────────────────────────┤
│ EXPRESSÃO + AÇÃO                                        │
│   conversation (11) language (12) actions (13)          │
│   voice/ (futuro)                                       │
├─────────────────────────────────────────────────────────┤
│ PROTEÇÃO + OBSERVAÇÃO                                   │
│   security (14) observability (15)                      │
└─────────────────────────────────────────────────────────┘
```

---

## Mapa número → pasta → submódulos

| # | Pasta | Subpastas principais | Papel |
|---|--------|----------------------|--------|
| 1 | `core/` | `models/`, `events/`, `validators/`, `internal/` | Kernel, lifecycle, registry |
| 2 | `configuration/` | `models/`, `sources/` | Config tipada + secrets |
| 3 | `neural/` | `models/` | Teia: nós, arestas, sinais |
| 4 | `event_bus/` | `models/` | Eventos formais |
| 5 | `memory/` | `models/` | Experiências |
| 6 | `knowledge/` | `models/` | Fatos / entidades / relações |
| 7 | `context/` | `models/` | Contexto cognitivo montado |
| 8 | `emotion/` | `models/` | Estado afetivo |
| 9 | `personality/` | `models/` | Traços e estilo estáveis |
| — | `identity/` | `brief/`, `relations/` | Narrativa: Kauã, PH, valores, brief |
| 10 | `reasoning/` | `models/` | Decisão estruturada |
| 11 | `conversation/` | `models/` | Sessão, intent, ResponseSpec |
| 12 | `language/` | `models/`, `providers/` | Texto final |
| 13 | `actions/` | `models/` | Ferramentas |
| 14 | `security/` | `models/` | AuthZ final |
| 15 | `observability/` | `models/` | Logs, métricas, health |
| 16 | `runtime/` | — | Orquestra; não é domínio |
| 17 | `bridge/` | `platforms/`, `continuity/`, `evolution/` | Discord+, cofre, evolução |
| F | `voice/` | (stub) | TTS futuro — só lê texto da Language |

---

## Teia Neural (ligações canônicas)

No `start()` do Runtime, cada módulo vira um **nó**. Arestas principais:

```text
configuration → core → runtime
runtime → neural → event_bus

memory ↔ knowledge ↔ context
context → emotion → personality → identity
personality → reasoning → conversation → language
language → bridge

security ─ (atravessa actions, bridge, configuration)
observability ─ (observa todos; não decide)
```

Sinais **não** substituem chamadas síncronas do pipeline.  
A teia documenta e propaga; o Runtime ainda orquestra o turno.

---

## Onde colocar coisa nova

| Quero... | Coloco em... |
|----------|----------------|
| Novo bot (Telegram) | `bridge/platforms/` |
| Novo fato sobre Yelena | `identity/` + seed Knowledge |
| Nova ferramenta | `actions/` + registry |
| Novo provedor de IA | `language/providers/` |
| Áudio / TTS | `voice/` (quando existir lógica real) |
| Grafo rico de amizades | futuro `relationship/` (hoje mínimo em identity) |
| Lore de mundo | futuro `world/` ou Knowledge |

**Não** crie módulo só para “completar número”.  
Só adicione pasta com responsabilidade clara.

---

## Fluxo de uma mensagem (resumo)

```text
Discord/HTTP
  → bridge | integration
  → runtime.pipeline (classifica complexidade)
  → emotion + personality + identity (brief)
  → memory / knowledge / context (se precisar)
  → reasoning (se precisar)
  → conversation → ResponseSpecification
  → language → texto
  → (futuro voice → áudio)
  → resposta no canal
```
