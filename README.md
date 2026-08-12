# Yelena V3

Plataforma modular de IA com identidade, personalidade, memória, raciocínio e segurança.

## Documentação de estrutura

- **[docs/MODULES.md](docs/MODULES.md)** — catálogo módulo → submódulo → pastas
- **[docs/STRUCTURE.md](docs/STRUCTURE.md)** — camadas + Teia Neural + regras

## Camadas (visão rápida)

```text
EDGE:           bridge (17), integration
ORQUESTRAÇÃO:   runtime (16), core (1), configuration (2)
SINAIS:         neural (3), event_bus (4)
COGNIÇÃO:       memory, knowledge, context, emotion, personality, identity, reasoning
EXPRESSÃO:      conversation, language, actions | voice (futuro)
PROTEÇÃO:       security, observability
```

## Produção

```bash
pip install -r requirements.txt
python main.py
```

| Env | Uso |
|-----|-----|
| `DISCORD_TOKEN` | bot online via Bridge |
| `YELENA_DISCORD_MODE` | `smart` / `mention` / `always` |
| `YELENA_HTTP_API_KEY` | protege POST /v1/process |

Health: `GET /health`

## Princípio

Runtime orquestra. Neural documenta e propaga.  
Cada módulo tem uma responsabilidade.  
Persona (Kauã, PH, valores) vive em `identity/` + Knowledge — não no Discord.
