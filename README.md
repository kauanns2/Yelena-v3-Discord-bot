# Yelena V3

Plataforma modular de IA com identidade, personalidade, memória, raciocínio e segurança arquitetural.

## Arquitetura (16 módulos)

Core · Configuration · Neural Web · Event Bus · Memory · Knowledge · Context · Emotion · Personality · Reasoning · Conversation · Language · Action · Security · Observability · Runtime

## Princípio

```
PENSAR → livre
EXECUTAR → autorização
```

O Runtime ativa só os módulos necessários por mensagem.

## Status

- [x] Módulos 1–16 (fundação)
- [x] Integration gateway + entrypoint de produção
- [x] Preparação para Render (infra only)

## Desenvolvimento

```bash
pip install -r requirements-dev.txt
pytest
```

```python
from app.runtime import YelenaRuntime

rt = YelenaRuntime()
rt.start()
print(rt.process("oi", user_id="kauanns2").text)
rt.stop()
```

## Produção / Render

```bash
pip install -r requirements.txt
python main.py
```

| Item | Valor |
|------|--------|
| Python | >= 3.11 (`runtime.txt`) |
| Build | `pip install -r requirements.txt` |
| Start | `python main.py` |
| Health | `GET /health` |

Detalhes: [`RENDER.md`](RENDER.md) · Contrato do intermediário: [`app/integration/README.md`](app/integration/README.md)

## Integração (intermediário existente)

```python
from app.integration import YelenaGateway, ProcessMessageRequest

gw = YelenaGateway()
gw.start()
resp = gw.process(ProcessMessageRequest(message="oi", user_id="discord:123"))
# resp.text → Discord via intermediário
gw.stop()
```

Ou HTTP: `POST /v1/process`

## Secrets

Nunca no Git. Use Environment do Render / host. Veja `.env.example`.
