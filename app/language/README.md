# Módulo 12 — Language & Response Generation

Transforma **ResponseSpecification** em texto linguístico.

## Separação

```
Conversation → o que dizer (ResponseSpecification)
Language     → como dizer (texto)
Provider     → motor de geração (local / API)
```

## Providers

- Abstração `LanguageProvider`
- `LocalTemplateProvider` — offline, testes, fallback
- Registry com seleção e fallback

## Uso

```python
from app.language import LanguageManager
from app.conversation import ConversationManager

lm = LanguageManager()
lm.start()

cm = ConversationManager()
cm.start()
session = cm.create_session()
_, spec = cm.process_message(session.id, "oi")

result = lm.generate_from_spec(spec)
print(result.text)
```

## Recursos

- InstructionBuilder a partir do spec
- Style / tone / length control
- Post-process (normalize + truncate)
- Fallback automático para provider local

## Integração futura

Providers reais (OpenAI, etc.) implementam `LanguageProvider` e registram no manager.
Secrets ficam no Configuration/Security — nunca no Language core.
