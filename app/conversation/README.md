# Módulo 11 — Conversation & Dialogue Management

Administra conversas e produz **ResponseSpecification** para o Language module.

## Separação

```
Conversation → organiza diálogo e especifica o que dizer
Language     → gera o texto
Reasoning    → decide
```

## Componentes

- Session / Participant / Turn
- Intent detection (leve)
- Topic stack
- ResponseSpecification

## Uso

```python
from app.conversation import ConversationManager

cm = ConversationManager()
cm.start()

session = cm.create_session(user_id="u1")
turn, spec = cm.process_message(
    session.id,
    "oi",
    context_summary=["usuário preocupado com o projeto"],
    emotion_summary={"valence": 0.1, "primary": "calm"},
)

print(spec.intent, spec.key_points, spec.tone)
```

## ResponseSpecification

Contrato para o Módulo 12:
- key_points
- tone / style_hints
- context_summary
- decision_summary
- clarification flags

## Fast path

Greetings e farewells geram spec curta — compatível com ativação seletiva.
