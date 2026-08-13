"""Adapter Discord — voz nativa, call e resposta falada na call."""

from __future__ import annotations

import logging
import os
import random
import re
from pathlib import Path
from typing import Any

from app.bridge.constants import PlatformId
from app.bridge.errors import PlatformError
from app.bridge.platforms.base import (
    InboundMessage,
    MessageHandler,
    OutboundMessage,
    PlatformAdapter,
)
from app.voice.call import (
    is_join_request,
    is_leave_request,
    join_and_speak,
    leave_voice,
    play_in_guild,
)
from app.voice.native_message import send_native_voice_message
from app.voice.stt import stt_available, transcribe_file

logger = logging.getLogger(__name__)

NAME_RE = re.compile(r"\byelena\b", re.I)
INTEREST_RE = re.compile(
    r"\b(yelena|ia|intelig[eê]ncia|mem[oó]ria|personalidade|emo[cç][aã]o|"
    r"sentir|pensar|arquitetura|seguran[cç]a|discord|projeto|áudio|audio|voz|call)\b",
    re.I,
)


class DiscordAdapter(PlatformAdapter):
    def __init__(self, token: str | None = None) -> None:
        self._token = token or os.getenv("DISCORD_TOKEN", "").strip()
        self._handler: MessageHandler | None = None
        self._client: Any = None
        self._started = False
        self._task: Any = None
        self._mode = (os.getenv("YELENA_DISCORD_MODE", "smart") or "smart").strip().lower()

    @property
    def platform_id(self) -> str:
        return PlatformId.DISCORD.value

    def set_handler(self, handler: MessageHandler) -> None:
        self._handler = handler

    def _should_respond(self, message: Any) -> bool:
        if self._mode == "always":
            return True
        try:
            if message.guild is None:
                return True
        except Exception:
            pass

        content = message.content or ""
        me = getattr(self._client, "user", None)
        if me is not None and me in getattr(message, "mentions", []):
            return True

        ref = getattr(message, "reference", None)
        if ref is not None and getattr(ref, "resolved", None) is not None:
            author = getattr(ref.resolved, "author", None)
            if author is not None and me is not None and author.id == me.id:
                return True

        if NAME_RE.search(content):
            return True
        if is_join_request(content) or is_leave_request(content):
            return True

        # se bot está na mesma call do autor, responde texto curto sem precisar do nome
        try:
            guild = message.guild
            author = message.author
            if (
                guild
                and guild.voice_client
                and guild.voice_client.is_connected()
                and getattr(author, "voice", None)
                and author.voice
                and author.voice.channel
                and guild.voice_client.channel
                and author.voice.channel.id == guild.voice_client.channel.id
            ):
                return True
        except Exception:
            pass

        if self._mode == "mention":
            return False
        if INTEREST_RE.search(content) and random.random() < 0.12:
            return True
        return False

    def _bot_in_same_call(self, message: Any) -> bool:
        try:
            guild = message.guild
            author = message.author
            if not guild or not guild.voice_client or not guild.voice_client.is_connected():
                return False
            if not getattr(author, "voice", None) or not author.voice or not author.voice.channel:
                return False
            return author.voice.channel.id == guild.voice_client.channel.id
        except Exception:
            return False

    async def start(self) -> None:
        if not self._token:
            raise PlatformError(
                "DISCORD_TOKEN not configured",
                context={"platform": self.platform_id},
            )
        if self._handler is None:
            raise PlatformError("Message handler not set for Discord adapter")

        try:
            import discord
        except ImportError as exc:
            raise PlatformError(
                "discord.py not installed. Add discord.py to requirements."
            ) from exc

        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        intents.voice_states = True

        adapter = self

        class YelenaClient(discord.Client):
            async def on_ready(self) -> None:  # type: ignore[override]
                adapter._started = True
                logger.info(
                    "discord adapter online user=%s mode=%s stt=%s",
                    str(self.user),
                    adapter._mode,
                    stt_available(),
                )

            async def on_message(self, message: discord.Message) -> None:  # type: ignore[override]
                if message.author.bot:
                    return
                if adapter._handler is None:
                    return

                content = (message.content or "").strip()

                # áudio anexo → STT (se disponível)
                if not content and message.attachments:
                    for att in message.attachments:
                        name = (att.filename or "").lower()
                        if name.endswith((".ogg", ".mp3", ".wav", ".m4a", ".webm")):
                            if not stt_available():
                                if NAME_RE.search(str(message.mentions)) or True:
                                    # só reage se mencão/nome implícito difícil — pede texto
                                    if adapter._should_respond(message) or adapter._bot_in_same_call(
                                        message
                                    ):
                                        await message.channel.send(
                                            "Recebi o áudio, mas STT ainda não está configurado "
                                            "(OPENAI_API_KEY). Por enquanto fala por texto na call."
                                        )
                                return
                            try:
                                path = Path(f"/tmp/yelena_in_{message.id}_{name}")
                                await att.save(str(path))
                                text = await transcribe_file(path)
                                path.unlink(missing_ok=True)
                                if text:
                                    content = text
                                    break
                            except Exception:
                                logger.exception("attachment STT failed")
                            return

                if not content:
                    return
                if not adapter._should_respond(message):
                    return

                if is_leave_request(content) and (
                    NAME_RE.search(content) or adapter._bot_in_same_call(message)
                ):
                    text = await leave_voice(self, message.guild)
                    await message.channel.send(text)
                    return

                if is_join_request(content):
                    from app.voice.manager import VoiceManager

                    vm = VoiceManager()
                    p = await vm.synthesize_async("Oi. Entrei na call. Pode falar comigo.")
                    audio = str(p) if p else None
                    status = await join_and_speak(self, message, audio)
                    await message.channel.send(status)
                    if audio:
                        Path(audio).unlink(missing_ok=True)
                    return

                inbound = InboundMessage(
                    text=content,
                    user_id=str(message.author.id),
                    channel_id=str(message.channel.id),
                    platform=PlatformId.DISCORD.value,
                    correlation_id=str(message.id),
                    metadata={
                        "guild_id": str(message.guild.id) if message.guild else None,
                        "author_name": str(message.author),
                        "in_voice_with_bot": adapter._bot_in_same_call(message),
                    },
                )

                try:
                    result = adapter._handler(inbound)
                    if hasattr(result, "__await__"):
                        outbound = await result  # type: ignore[misc]
                    else:
                        outbound = result
                    if not outbound:
                        return

                    # se estamos na mesma call → responde em voz no canal de voz
                    if adapter._bot_in_same_call(message) and outbound.text:
                        from app.voice.manager import VoiceManager

                        vm = VoiceManager()
                        audio_path = await vm.synthesize_async(outbound.text)
                        if audio_path and message.guild:
                            played = await play_in_guild(message.guild, audio_path)
                            Path(audio_path).unlink(missing_ok=True)
                            if played:
                                # opcional: eco texto curto no chat
                                if os.getenv("YELENA_VOICE_CHAT_ECHO", "false").lower() in {
                                    "1",
                                    "true",
                                    "yes",
                                }:
                                    await message.channel.send(outbound.text[:1900])
                                return

                    await adapter._send_outbound(message.channel, outbound)
                except Exception:
                    logger.exception("discord handler failed")
                    try:
                        await message.channel.send(
                            "Tive um problema interno agora. Tenta de novo em instantes."
                        )
                    except Exception:
                        pass

        self._client = YelenaClient(intents=intents)
        import asyncio

        self._task = asyncio.create_task(self._client.start(self._token))
        logger.info("discord adapter starting mode=%s", self._mode)

    async def _send_outbound(self, channel: Any, outbound: OutboundMessage) -> None:
        text = (outbound.text or "")[:1900]
        audio = outbound.audio_path

        if audio and Path(audio).is_file():
            try:
                ok = await send_native_voice_message(channel, audio, fallback_text=text)
                if not ok and text:
                    await channel.send(text)
            finally:
                Path(audio).unlink(missing_ok=True)
            return

        if text:
            await channel.send(text)

    async def stop(self) -> None:
        self._started = False
        if self._client is not None:
            try:
                await self._client.close()
            except Exception:
                logger.exception("error closing discord client")
        if self._task is not None:
            self._task.cancel()
            self._task = None

    async def send(self, message: OutboundMessage) -> None:
        if self._client is None:
            raise PlatformError("Discord client not started")
        channel = self._client.get_channel(int(message.channel_id))
        if channel is None:
            channel = await self._client.fetch_channel(int(message.channel_id))
        await self._send_outbound(channel, message)

    def health(self) -> dict[str, Any]:
        return {
            "platform": self.platform_id,
            "status": "online" if self._started else "offline",
            "token_configured": bool(self._token),
            "mode": self._mode,
            "stt": stt_available(),
        }
