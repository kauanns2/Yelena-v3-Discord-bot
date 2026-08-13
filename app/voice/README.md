# Voice

## Perfil alvo (Yelena)

Feminina ~20–23, russa em pt-BR, sotaque russo leve, conversa de call Discord (não narradora).

Hoje a síntese usa **edge-tts** (`pt-BR-FranciscaNeural`) com rate/pitch ajustados.  
Isso **não** clona voz real — é a melhor aproximação gratuita.  
Quando houver amostra de voz, pluga clone (ElevenLabs / RVC / etc.) no `VoiceManager`.

## Call

1. Entre num canal de voz
2. Peça para ela entrar (linguagem natural)
3. Enquanto ela estiver na **mesma call**, mensagens de texto viram **fala no canal de voz**
4. Áudio anexo no chat pode virar texto se `OPENAI_API_KEY` estiver setada (Whisper)

Escuta contínua do microfone da call (STT em tempo real no voice channel) ainda é limitada no Discord bot — o caminho estável atual é texto na call → resposta em voz, ou áudio no chat → STT.

## Env

```text
YELENA_VOICE_ENABLED=true
YELENA_TTS_VOICE=pt-BR-FranciscaNeural
YELENA_TTS_RATE=+6%
YELENA_TTS_PITCH=+3Hz
YELENA_VOICE_AUTO=0
OPENAI_API_KEY=   # opcional, STT Whisper
```
