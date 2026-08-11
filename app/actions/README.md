# Módulo 13 — Action & Tool Execution

Executa ações controladas através de ferramentas.

## Princípio

```
Reasoning = decide
Action    = executa (com autorização)
Language  = comunica
```

**Pensar ≠ Executar.**

## Fluxo

```
ActionRequest
  → validate arguments
  → permission / risk check
  → confirmation (se necessário)
  → execute / dry-run
  → ActionResult
```

## Uso

```python
from app.actions import ActionManager
from app.actions.models.request import ActionRequest

am = ActionManager()
am.start()

result = am.execute(ActionRequest(
    tool_id="echo",
    arguments={"message": "olá"},
))
print(result.success, result.output)
```

## Segurança

- Tools de alto risco exigem `confirmed=True`
- Path traversal bloqueado na validação
- Dry-run sem side effects
- Autoridade final de segurança: Módulo 14

## Adapters externos

Discord, GitHub, filesystem etc. **não** ficam no núcleo.
Registram-se como tools via `register_tool`.
