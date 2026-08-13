# Voice

## Chat — mensagem de voz nativa

Quando você pede áudio, a Yelena tenta enviar **voice message** do Discord (bolinha de áudio), não um arquivo solto com texto.

```text
Yelena manda um áudio
```

## Call (canal de voz)

1. Entre numa call no servidor
2. `Yelena entra na call` ou `Yelena liga`
3. Ela conecta no seu canal e tenta falar
4. `Yelena sai da call` para desconectar

Permissões do bot no canal de voz:
- Conectar
- Falar
- Usar VAD (opcional)

## Env

```text
YELENA_VOICE_ENABLED=true
YELENA_TTS_VOICE=pt-BR-FranciscaNeural
YELENA_VOICE_AUTO=0
```

## Dependências

- edge-tts (síntese)
- imageio-ffmpeg (converte + toca)
- PyNaCl (voice websocket Discord)
