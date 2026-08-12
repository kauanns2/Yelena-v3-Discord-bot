# Yelena V3

Plataforma modular de IA com identidade, personalidade, memória, raciocínio e segurança arquitetural.

## Arquitetura

**Módulos 1–16** — núcleo cognitivo e operacional  
**Módulo 17 — Bridge** — plataformas (Discord+), continuidade, evolução, resiliência

```
Discord / futuros bots
        ↓
   Bridge (17)
        ↓
 Runtime (16) + módulos 1–15
```

## Status

- [x] Módulos 1–16
- [x] Módulo 17 — Platform Bridge, Continuity & Evolution
- [x] Entrypoint de produção (Render)

## Produção / Render

```bash
pip install -r requirements.txt
python main.py
```

| Env | Uso |
|-----|-----|
| `DISCORD_TOKEN` | deixa o bot Discord online via Bridge |
| `YELENA_HTTP_API_KEY` | protege `POST /v1/process` |
| `YELENA_CONTINUITY_DIR` | pasta do cofre de continuidade |

Health: `GET /health`

## Discord online

1. Crie o bot no [Discord Developer Portal](https://discord.com/developers/applications)
2. Ative **Message Content Intent**
3. No Render, adicione `DISCORD_TOKEN=...`
4. Redeploy

O Bridge sobe o adapter automaticamente no startup.

## Continuidade

O Módulo 17 guarda snapshots para uso futuro, reduzindo falhas quando um módulo pedir dado que não está na RAM.
