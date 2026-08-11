# Integration Layer (borda)

Esta camada permite que o **intermediário Discord + IA já existente** use a Yelena V3 **sem** colocar Discord dentro do Core.

## O que NÃO está neste repositório

- Bot Discord
- Tokens Discord / OpenAI
- Protocolo interno completo do intermediário

Se o intermediário mudar de transporte, só a borda muda.

## Contratos

### Python (import direto)

```python
from app.integration import YelenaGateway, ProcessMessageRequest

gw = YelenaGateway()
gw.start()

resp = gw.process(ProcessMessageRequest(
    message="oi",
    user_id="discord:123",
    session_id="channel:456",
    channel="discord",
    correlation_id="msg:789",
))

print(resp.text)          # resposta para o Discord
print(resp.session_id)    # reutilizar nas próximas mensagens
print(resp.to_dict())     # JSON-friendly

gw.stop()
```

### HTTP JSON

```http
POST /v1/process
Content-Type: application/json
X-Api-Key: <YELENA_HTTP_API_KEY opcional>

{
  "message": "oi",
  "user_id": "discord:123",
  "session_id": "channel:456",
  "channel": "discord",
  "correlation_id": "msg:789"
}
```

Resposta:

```json
{
  "text": "Oi.",
  "request_id": "...",
  "session_id": "...",
  "complexity": "trivial",
  "modules_used": ["conversation", "language"],
  "confidence": 0.55,
  "metadata": {}
}
```

Health:

```http
GET /health
```

## Fluxo

```
Discord User
    ↓
Intermediário existente (Discord + IA + Git)
    ↓  HTTP ou import Python
YelenaGateway / HTTP API
    ↓
YelenaRuntime.process(...)
    ↓
RuntimeResponse → ProcessMessageResponse
    ↓
Intermediário → Discord
```

## Secrets

- Tokens Discord / providers ficam no intermediário ou em env do host
- Este serviço só precisa de `YELENA_HTTP_API_KEY` (opcional) e `PORT`
- Nunca commitar secrets
