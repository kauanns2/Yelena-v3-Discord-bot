# Módulo 14 — Security & Authorization

Autoridade independente de segurança da Yelena.

## Princípio

```
Request → Identity → Authentication → Authorization → Policy → Risk → Decision
```

Nenhum módulo declara sozinho "pode executar".

## Separação

| Camada | Papel |
|--------|--------|
| Action permissions | checagem local de tool/risk |
| **Security** | autoridade final |

## Admin principal

Você é o administrador.
A Yelena pode:
- questionar
- alertar
- recomendar

Ela **não** pode:
- remover sua autoridade
- alterar suas permissões
- esconder informações de você

## Uso

```python
from app.security import SecurityManager
from app.security.constants import RiskLevel

sec = SecurityManager(admin_id="kauanns2")
sec.start()

decision = sec.authorize(
    "kauanns2",
    resource="action",
    action="execute",
    risk=RiskLevel.HIGH,
)
print(decision.effect, decision.reason)
```

## Recursos

- RBAC (roles/permissions)
- SecurityGate fail-closed
- Audit append-only
- SecretStore (valores nunca em logs)
- Emergency lock
- Challenge em ações high/critical
