# Módulo 17 — Platform Bridge, Continuity & Evolution

Camada de **borda** da Yelena V3.

## Papel

```
Plataformas (Discord, futuros bots)
        ↓
    Bridge (17)
        ↓
 Runtime + módulos 1–16
```

O Bridge **não** substitui Memory, Personality, Reasoning, etc.
Ele:

1. Aceita **qualquer plataforma** via `PlatformAdapter`
2. Guarda **continuidade** (snapshots) para uso futuro
3. Registra **evolução** (ledger)
4. Aplica **resiliência** para reduzir erros em cascata

## Discord

Com `DISCORD_TOKEN` no ambiente, o adapter sobe junto com o Runtime.

```
Mensagem Discord → Bridge → Runtime.process → resposta → Discord
```

## Continuidade

```python
bridge.deposit("session", "user:123", session_id)
session = bridge.recall("session", "user:123")
```

## Novas plataformas

Implemente `PlatformAdapter` e registre em `PlatformRegistry`.
Não precisa alterar os módulos 1–16.
