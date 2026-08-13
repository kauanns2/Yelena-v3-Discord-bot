# Módulo Voice — Yelena

Módulo **especializado** em voz e call. Não mistura com Language nem Discord core.

## Responsabilidades

- Perfil vocal da Yelena
- TTS (hoje edge-tts; depois clone)
- Entrar / sair / falar em canal de voz
- STT opcional (Whisper)
- **Não** envia arquivo de áudio no chat

## Comportamento

| Situação | O que acontece |
|----------|----------------|
| Pediu áudio **fora** da call | Resposta em texto + orienta entrar na call |
| Pediu áudio **na** call | Fala no canal de voz |
| Texto enquanto bot está na mesma call | Responde **falando** na call |

## Perfil vocal

Referência de **clareza / juventude** (tipo voz jovem e limpa), **puxada para realismo**:

- ~20–23 anos, feminina
- Sem tom de anime / dublagem exagerada
- Call de Discord, não estúdio
- pt-BR com leve coloração; clone futuro pode refinar sotaque russo

## Estrutura

```text
app/voice/
  profile.py      # identidade vocal
  providers/      # TTS (edge, futuro clone)
  call.py         # join / play / leave
  stt.py          # opcional
  manager.py      # fachada do módulo
  native_message.py  # legado (desativado no envio de chat)
```

## Env

```text
YELENA_VOICE_ENABLED=true
YELENA_TTS_VOICE=pt-BR-FranciscaNeural
YELENA_TTS_RATE=+2%
YELENA_TTS_PITCH=+5Hz
YELENA_VOICE_AUTO=0
OPENAI_API_KEY=   # STT opcional
```
