# Yelena V3

Plataforma modular de IA com identidade, personalidade, memória, raciocínio e segurança arquitetural.

## Arquitetura (16 módulos)

1. Core & Kernel
2. Configuration
3. Neural Web
4. Event Bus
5. Memory System
6. Knowledge System
7. Cognitive Context
8. Emotion & Affective State
9. Personality & Behavioral Identity
10. Reasoning & Decision
11. Conversation & Dialogue
12. Language & Response Generation
13. Action & Tool Execution
14. Security & Authorization
15. Observability & Diagnostics
16. Runtime & Orchestration

## Princípio central

Não executar todos os módulos em toda mensagem.
O Runtime combina apenas o necessário conforme intenção, contexto, complexidade e risco.

```
PENSAR → livre
EXECUTAR → autorização
```

## Status

- [x] Módulos 1–16 (fundação)
- [x] Integration gateway + entrypoint de produção
- [ ] Intermediário Discord (externo — já existente, não duplicar)

## Uso local (Runtime)

```bash
pip install -r requirements.txt
pytest
```

```python
from app.runtime import YelenaRuntime

rt = YelenaRuntime()
rt.start()
print(rt.process("oi", user_id="kauanns2").text)
rt.stop()
```

## Integração com o intermediário existente

O bot Discord **não** vive neste Core. O intermediário chama a Yelena assim:

### Opção A — Python

```python
from app.integration import YelenaGateway, ProcessMessageRequest

gw = YelenaGateway()
gw.start()
resp = gw.process(ProcessMessageRequest(
    message="oi",
    user_id="discord:123",
    session_id="channel:456",
    channel="discord",
))
# resp.text → enviar de volta ao Discord
gw.stop()
```

### Opção B — HTTP (Render / produção)

```bash
python main.py
# ou: uvicorn main:app --host 0.0.0.0 --port $PORT
```

```http
POST /v1/process
Content-Type: application/json

{"message": "oi", "user_id": "discord:123", "channel": "discord"}
```

```http
GET /health
```

Documentação completa: `app/integration/README.md`

## Render

| Campo | Valor |
|-------|--------|
| Runtime | Python 3.11+ |
| Build | `pip install -r requirements.txt` |
| Start | `python main.py` |
| Health check | `GET /health` |
| Env | `PORT` (automático), `YELENA_HTTP_API_KEY` (opcional), `YELENA_LOG_LEVEL` |

**Não** coloque token Discord neste serviço se o intermediário já o possui.

## Secrets

Nunca commitar tokens. Use `.env.example` só como referência de nomes.
