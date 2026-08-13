"""Canal de voz Discord — join com escuta, fala, leave."""

from __future__ import annotations

import logging
import os
import re
from pathlib import Path
from typing import Any, Awaitable, Callable

from app.voice.listen import CallListener
from app.voice.stt import stt_available, stt_backend_name

logger = logging.getLogger(__name__)

JOIN_RE = re.compile(
    r"(?:"
    r"\b(?:liga|ligar|join)\b"
    r"|(?:entra|entre|vem|conecta|conectar)\s+(?:na|no|pra|para)?\s*"
    r"(?:call|cal|cail|liga[cç][aã]o|voice|voz|canal de voz|sala)\b"
    r"|(?:call|cal|liga[cç][aã]o)\b"
    r")",
    re.I,
)
LEAVE_RE = re.compile(
    r"(?:sai|sair|desconecta|leave|hang\s*up).*(?:call|cal|liga[cç][aã]o|voz)?"
    r"|\b(?:leave|disconnect)\b",
    re.I,
)

_LISTENERS: dict[int, CallListener] = {}


def is_join_request(text: str) -> bool:
    t = (text or "").strip()
    if not t:
        return False
    return bool(JOIN_RE.search(t))


def is_leave_request(text: str) -> bool:
    return bool(LEAVE_RE.search(text or ""))


def _ffmpeg() -> str | None:
    try:
        import imageio_ffmpeg

        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return None


async def leave_voice(client: Any, guild: Any) -> str:
    if guild is None:
        return "Não estou em um servidor."
    gid = guild.id
    _LISTENERS.pop(gid, None)
    vc = guild.voice_client
    if vc is None:
        return "Não estou em nenhuma call."
    try:
        if hasattr(vc, "stop_listening"):
            try:
                vc.stop_listening()
            except Exception:
                pass
        await vc.disconnect(force=True)
        return "Saí da call."
    except Exception:
        logger.exception("leave voice failed")
        return "Não consegui sair da call."


async def play_in_guild(guild: Any, audio_path: str | Path) -> bool:
    import discord

    if guild is None:
        return False
    vc = guild.voice_client
    if vc is None or not vc.is_connected():
        return False
    path = Path(audio_path)
    if not path.is_file():
        return False
    ffmpeg = _ffmpeg()
    if ffmpeg is None:
        return False

    listener = _LISTENERS.get(guild.id)
    if listener:
        listener.pause()

    try:
        source = discord.FFmpegPCMAudio(str(path), executable=ffmpeg, options="-vn")

        def _after(err: Exception | None) -> None:
            if listener:
                listener.resume()
            if err:
                logger.error("play error: %s", err)

        if vc.is_playing():
            vc.stop()
        vc.play(source, after=_after)
        return True
    except Exception:
        if listener:
            listener.resume()
        logger.exception("play_in_guild failed")
        return False


async def join_and_listen(
    client: Any,
    message: Any,
    *,
    on_user_text: Callable[[str, Any], Awaitable[None]] | None = None,
    greeting_audio: str | Path | None = None,
) -> str:
    author = message.author
    if not getattr(author, "voice", None) or author.voice is None or author.voice.channel is None:
        return "Entra numa call antes — aí eu conecto com você."

    channel = author.voice.channel
    guild = message.guild
    if guild is None:
        return "Call só funciona em servidor, não em DM."

    me = guild.me or guild.get_member(client.user.id)
    if me is not None:
        perms = channel.permissions_for(me)
        if not getattr(perms, "connect", True) or not getattr(perms, "speak", True):
            return "Não tenho permissão de conectar/falar nesse canal de voz."

    vc = guild.voice_client
    recv_cls = None
    try:
        from discord.ext import voice_recv

        recv_cls = voice_recv.VoiceRecvClient
    except Exception:
        logger.warning("discord-ext-voice-recv não disponível — call sem escuta")

    try:
        if vc is not None and vc.is_connected():
            if vc.channel.id != channel.id:
                await vc.move_to(channel)
        else:
            if recv_cls is not None:
                vc = await channel.connect(cls=recv_cls)
            else:
                vc = await channel.connect()
    except Exception:
        logger.exception("voice connect failed")
        return "Não consegui entrar na call. Confere permissão Conectar/Falar."

    listen_ok = False
    if recv_cls is not None and on_user_text is not None and stt_available():
        try:
            from discord.ext import voice_recv
            import asyncio

            listener = CallListener(
                on_user_text,
                bot_user_id=getattr(client.user, "id", None),
            )
            listener.set_loop(asyncio.get_running_loop())
            _LISTENERS[guild.id] = listener

            def _cb(user: Any, data: Any) -> None:
                listener.on_packet(user, data)

            vc.listen(voice_recv.BasicSink(_cb))
            listen_ok = True
        except Exception:
            logger.exception("start listen failed")

    if greeting_audio and Path(greeting_audio).is_file():
        await play_in_guild(guild, greeting_audio)

    backend = stt_backend_name()
    if listen_ok:
        extra = ""
        if backend == "google_free":
            extra = " (escuta gratuita — pode falhar se o Google limitar)"
        return (
            "Entrei na call e tô te ouvindo"
            + extra
            + ". Fala no microfone — eu transformo em texto, corrijo e respondo em voz."
        )
    return "Entrei na call. Escuta do microfone falhou — tenta de novo ou usa texto por enquanto."


async def join_and_speak(
    client: Any,
    message: Any,
    audio_path: str | Path | None,
    *,
    speak_text_fallback: str = "",
) -> str:
    return await join_and_listen(
        client,
        message,
        on_user_text=None,
        greeting_audio=audio_path,
    )
