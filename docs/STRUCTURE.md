# Yelena V3 — Mapa de estrutura

Convenção:

```text
módulo/
  README.md          # o que o módulo faz / não faz
  manager.py         # fachada pública
  models/            # dados
  <submódulo>/       # pasta só se houver grupo claro
```

Não espalhe lógica de domínio no Runtime ou no Bridge.

---

## Camadas

```text
EDGE (borda)
  bridge/          # M17 plataformas, continuidade, evolução, resiliência
  integration/     # HTTP gateway

ORQUESTRAÇÃO
  runtime/         # M16 pipeline seletivo
  core/            # M1 kernel, lifecycle, registry
  configuration/   # M2 config tipada

INFRA DE SINAIS
  neural/          # M3 teia
  event_bus/       # M4 eventos

COGNIÇÃO / IDENTIDADE
  memory/          # M5 experiências
  knowledge/       # M6 fatos estruturados
  context/         # M7 contexto cognitivo
  emotion/         # M8 afeto
  personality/     # M9 traços estáveis
  identity/        # identidade narrativa (Kauã, PH, brief)
  reasoning/       # M10 decisão

EXPRESSÃO / AÇÃO
  conversation/    # M11 diálogo
  language/        # M12 texto
  actions/         # M13 ferramentas

PROTEÇÃO / OBSERVAÇÃO
  security/        # M14
  observability/   # M15
```

---

## Módulos (número → pasta → subpastas)

| # | Pasta | Submódulos / pastas | Responsabilidade |
|---|--------|---------------------|------------------|
| 1 | `core/` | `models/`, `events/`, `validators/`, `internal/` | Lifecycle, registry, DI |
| 2 | `configuration/` | `models/`, `sources/` | Config + secrets |
| 3 | `neural/` | `models/` | Topologia + sinais |
| 4 | `event_bus/` | `models/` | Pub/sub formal |
| 5 | `memory/` | `models/` | Experiências |
| 6 | `knowledge/` | `models/` | Fatos / entidades |
| 7 | `context/` | `models/` | Contexto montado |
| 8 | `emotion/` | `models/` | Estado afetivo |
| 9 | `personality/` | `models/` | Traços / estilo |
| — | `identity/` | `brief/`, `relations/` | Quem ela é (narrativa) |
| 10 | `reasoning/` | `models/` | Decisão estruturada |
| 11 | `conversation/` | `models/` | Sessão / intent / spec |
| 12 | `language/` | `models/`, `providers/` | Texto final |
| 13 | `actions/` | `models/` | Tools |
| 14 | `security/` | `models/` | AuthZ final |
| 15 | `observability/` | `models/` | Logs, métricas, health |
| 16 | `runtime/` | — | Orquestra 1–15 + identity |
| 17 | `bridge/` | `platforms/`, `continuity/`, `evolution/` | Discord+ e cofre |

---

## Fluxo de uma mensagem

```text
Discord/HTTP
  → bridge ou integration
  → runtime.pipeline (complexidade)
  → emotion + personality + identity brief
  → memory/knowledge/context (se precisar)
  → reasoning (se precisar)
  → conversation → ResponseSpecification
  → language (texto)
  → resposta
```

---

## Regras ao mexer no código

1. Um módulo não importa o miolo de outro se existir interface no manager.
2. Discord só em `bridge/platforms/`.
3. Secrets só via Configuration / env — nunca no Git.
4. Persona narrativa vive em `identity/` + seed no Knowledge.
5. Evolução registra em `bridge/evolution/`; mudança de trait passa por Personality com limite.
6. Voice/áudio (futuro): pasta `app/voice/` — consome texto da Language, não redefine persona.

---

## Futuro organizado (quando precisar)

```text
app/voice/           # TTS / áudio
app/relationship/    # grafo rico de vínculos (hoje mínimo em identity)
app/world/           # lore expandido
```

Adicionar pasta **só** quando houver responsabilidade clara. Não criar módulo só para “parecer completo”.
