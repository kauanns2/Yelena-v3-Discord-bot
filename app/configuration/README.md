# Módulo 2 — Configuration

Sistema centralizado de configuração da Yelena V3.

## Princípio

Nenhum módulo deve fazer:

```python
os.getenv("...")
```

Todos recebem configuração tipada via `ConfigurationManager`.

## Fontes e precedência

```
defaults  <  files  <  environment  <  memory overrides
```

## Secrets

Secrets usam prefixo `YELENA_SECRET_` e nunca aparecem em logs.

Exemplo:
```
YELENA_SECRET_DISCORD_TOKEN=...
YELENA_SECRET_OPENAI_API_KEY=...
```

## Uso

```python
from app.configuration import ConfigurationManager

manager = ConfigurationManager(environment="development")
config = manager.load()

print(config.application.name)
print(config.core.shutdown_timeout)

# Secret
token = manager.get_secret("discord_token")
```

## Variáveis de ambiente públicas

```
YELENA_APPLICATION_DEBUG=true
YELENA_CORE_SHUTDOWN_TIMEOUT=30
YELENA_LOGGING_LEVEL=INFO
```

## Integração com Core

O Configuration é carregado cedo no bootstrap e fornecido aos módulos via contratos.
Não depende do Kernel para funcionar.
