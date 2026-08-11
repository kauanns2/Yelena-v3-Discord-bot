# Deploy no Render

O Render é **apenas infraestrutura**. Ele não contém lógica da Yelena.

```
GitHub  →  Render (Python env)  →  main.py  →  YelenaGateway  →  YelenaRuntime  →  módulos
```

## Configuração do serviço (Web Service)

| Campo | Valor |
|-------|--------|
| Environment | Python 3 |
| Region | a de sua escolha |
| Branch | `main` |
| Root Directory | *(vazio — raiz do repo)* |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `python main.py` |
| Health Check Path | `/health` |

Python mínimo: **3.11** (`runtime.txt` pinado em 3.11.11).

## Variáveis de ambiente (Environment)

Defina no painel do Render — **nunca no Git**:

| Variável | Obrigatória | Descrição |
|----------|-------------|-----------|
| `PORT` | automática | Porta HTTP (Render define) |
| `YELENA_ENVIRONMENT` | recomendada | `production` |
| `YELENA_LOG_LEVEL` | opcional | `INFO` (padrão) |
| `YELENA_HTTP_API_KEY` | recomendada | Protege `POST /v1/process` |
| `YELENA_SECRET_*` | conforme uso | Secrets lidos pelo Configuration |

Exemplos de secret (prefixo `YELENA_SECRET_`):

```
YELENA_SECRET_OPENAI_API_KEY=...
```

Tokens **Discord** devem permanecer no intermediário existente, a menos que você decida explicitamente o contrário.

## Endpoints

- `GET /` — info do serviço
- `GET /health` — health do Runtime/módulos
- `POST /v1/process` — mensagem → resposta (JSON)

Contrato completo: `app/integration/README.md`

## O que o Render NÃO faz

- Não inicia módulos individualmente
- Não guarda cópia da arquitetura da Yelena
- Não substitui Configuration/Secrets
- Não é o bot Discord

## Troca de host

Qualquer servidor que rode:

```bash
pip install -r requirements.txt
python main.py
```

com `PORT` definido é suficiente. A aplicação não depende do Render.
