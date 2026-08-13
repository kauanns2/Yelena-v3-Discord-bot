"""Canal de voz Discord — entrar, falar, sair, responder na call."""

from __future__ import annotations

import logging
import os
import re
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

JOIN_RE = re.compile(
    r"\b(liga|ligar|entre na call|entra na call|entra no voice|join|"
    r"vem pra call|vem na call|conecta na call|entra na sala)\b",
    re.I,
)
LEAVE_RE = re.compile(r"\b(sai da call|sair da call|desconecta|leave|hang up)\b", re.I)

# guild_id -> voice client ref helper via discord guild.voice_client


def is_join_request(text: str) -> bool:
    return bool(JOIN_RE.search(text or ""))


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
    vc = guild.voice_client
    if vc is None:
        return "Não estou em nenhuma call."
    try:
        await vc.disconnect(force=True)
        return "Saí da call."
    except Exception:
        logger.exception("leave voice failed")
        return "Não consegui sair da call."


async def play_in_guild(guild: Any, audio_path: str | Path) -> bool:
    """Toca áudio no voice client atual do guild."""
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
    try:
        source = discord.FFmpegPCMAudio(str(path), executable=ffmpeg, options="-vn")
        if vc.is_playing():
            vc.stop()
        vc.play(source)
        return True
    except Exception:
        logger.exception("play_in_guild failed")
        return False


async def join_and_speak(
    client: Any,
    message: Any,
    audio_path: str | Path | None,
    *,
    speak_text_fallback: str = "",
) -> str:
    import discord

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
    try:
        if vc is None or not vc.is_connected():
            vc = await channel.connect()
        elif vc.channel.id != channel.id:
            await vc.move_to(channel)
    except Exception:
        logger.exception("voice connect failed")
        return "Não consegui entrar na call. Confere permissão Conectar/Falar."

    if audio_path and Path(audio_path).is_file():
        ok = await play_in_guild(guild, audio_path)
        if ok:
            return "Entrei na call. Pode falar comigo por texto que eu respondo em voz — ou manda áudio no chat."
        return "Entrei na call, mas não consegui tocar o áudio."

    return "Entrei na call. Pode falar comigo por texto que eu respondo em voz."
