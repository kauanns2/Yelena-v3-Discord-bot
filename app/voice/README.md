# Voice

## Chat — mensagem de voz nativa

Quando o usuário pede áudio, a Yelena tenta enviar voice message nativa do Discord (player de áudio), sem texto + anexo juntos.

## Call (canal de voz)

Ela pode entrar no canal de voz em que o usuário estiver e falar, e também sair quando pedido em linguagem natural.

Permissões no canal de voz: Conectar e Falar.

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
