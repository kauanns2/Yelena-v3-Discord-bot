# Yelena V3

Plataforma modular de IA com identidade, personalidade, memória, raciocínio e segurança.

## Mapa rápido

Veja **[docs/STRUCTURE.md](docs/STRUCTURE.md)** — módulo → submódulos → pastas.

```text
EDGE:        bridge, integration
ORQUESTRA:   runtime, core, configuration
SINAIS:      neural, event_bus
COGNIÇÃO:    memory, knowledge, context, emotion, personality, identity, reasoning
EXPRESSÃO:   conversation, language, actions
PROTEÇÃO:    security, observability
```

## Identidade

`app/identity/` guarda o **brief** e relações canônicas (Kauã, PH).
No start do Runtime, esses fatos são semeados no Knowledge.

## Produção

```bash
pip install -r requirements.txt
python main.py
```

Env importantes:

| Var | Uso |
|-----|-----|
| `DISCORD_TOKEN` | bot online via Bridge |
| `YELENA_DISCORD_MODE` | `smart` / `mention` / `always` |
| `YELENA_HTTP_API_KEY` | protege `/v1/process` |

## Status

- [x] Módulos 1–17
- [x] Identity layer (brief + Kauã/PH)
- [ ] Provider LLM real no Language
- [ ] Voice/áudio (futuro `app/voice/`)
