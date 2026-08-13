# Módulo Voice

## Call (fluxo principal)

1. Você entra na call
2. Pede pra Yelena entrar
3. Você **fala no microfone**
4. Ela escuta → STT (Whisper) → corrige texto → pensa → **responde falando na call**

Requisito: `OPENAI_API_KEY` no Render (Whisper).

## Chat

- Pediu áudio **fora** da call → tenta **mensagem de voz nativa** do Discord (não arquivo solto)
- **Na** call → só fala no canal de voz

## Env

```text
YELENA_VOICE_ENABLED=true
YELENA_TTS_VOICE=pt-BR-FranciscaNeural
OPENAI_API_KEY=sk-...
```
