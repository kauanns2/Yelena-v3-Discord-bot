# Voice

## O que faz

- Gera áudio (TTS) a partir do texto da Language
- Discord envia o arquivo no chat quando o usuário pede áudio

## Ativar no Render

```text
YELENA_VOICE_ENABLED=true
YELENA_TTS_VOICE=pt-BR-FranciscaNeural
YELENA_VOICE_AUTO=0
```

`YELENA_VOICE_AUTO=0` → só quando pedirem áudio/voz  
`YELENA_VOICE_AUTO=0.15` → ~15% das respostas em áudio sem pedir

## Vozes pt-BR (edge-tts)

- `pt-BR-FranciscaNeural` (feminina, padrão)
- `pt-BR-AntonioNeural` (masculina)

## Fase 2 — ligar na call (canal de voz)

Entrar no voice channel e falar exige `ffmpeg` + `PyNaCl` no servidor.  
No Render free isso é frágil. Por isso a fase 1 é **áudio no chat** (arquivo), que já funciona com a permissão de anexos do bot.

## Não faz

- Personalidade / emoção (só lê o texto pronto)
