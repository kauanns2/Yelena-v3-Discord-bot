"""Adapter Discord — call com escuta + voz nativa no chat (sem anexo solto)."""

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
    join_and_listen,
    leave_voice,
    play_in_guild,
)
from app.voice.native_message import send_native_voice_message
from app.voice.stt import stt_available, transcribe_file
from app.voice.wants import wants_audio

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
        if self._bot_in_same_call(message):
            return True
        if self._mode == "mention":
            return False
        if INTEREST_RE.search(content) and random.random() < 0.12:
            return True
        return False

    async def _handle_voice_utterance(self, text: str, member: Any, guild: Any) -> None:
        """Texto da call → Runtime → fala na call."""
        if self._handler is None or not text:
            return
        inbound = InboundMessage(
            text=text,
            user_id=str(member.id),
            channel_id=str(guild.id),
            platform=PlatformId.DISCORD.value,
            metadata={"in_voice_with_bot": True, "source": "voice_call"},
        )
        try:
            result = self._handler(inbound)
            outbound = await result if hasattr(result, "__await__") else result
            if not outbound or not outbound.text:
                return
            from app.voice.manager import VoiceManager

            vm = VoiceManager()
            audio = await vm.synthesize_async(outbound.text)
            if audio:
                await play_in_guild(guild, audio)
                Path(audio).unlink(missing_ok=True)
        except Exception:
            logger.exception("voice utterance handle failed")

    async def start(self) -> None:
        if not self._token:
            raise PlatformError("DISCORD_TOKEN not configured")
        if self._handler is None:
            raise PlatformError("Message handler not set")

        import discord

        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        intents.voice_states = True

        adapter = self

        class YelenaClient(discord.Client):
            async def on_ready(self) -> None:  # type: ignore[override]
                adapter._started = True
                logger.info(
                    "discord online user=%s stt=%s",
                    str(self.user),
                    stt_available(),
                )

            async def on_message(self, message: discord.Message) -> None:  # type: ignore[override]
                if message.author.bot or adapter._handler is None:
                    return

                content = (message.content or "").strip()

                if not content and message.attachments and stt_available():
                    for att in message.attachments:
                        name = (att.filename or "").lower()
                        if name.endswith((".ogg", ".mp3", ".wav", ".m4a", ".webm")):
                            try:
                                path = Path(f"/tmp/yelena_in_{message.id}_{name}")
                                await att.save(str(path))
                                text = await transcribe_file(path)
                                path.unlink(missing_ok=True)
                                if text:
                                    content = text
                                    break
                            except Exception:
                                logger.exception("STT attach failed")
                            break

                if not content or not adapter._should_respond(message):
                    return

                if is_leave_request(content) and (
                    NAME_RE.search(content) or adapter._bot_in_same_call(message)
                ):
                    await message.channel.send(await leave_voice(self, message.guild))
                    return

                if is_join_request(content):
                    from app.voice.manager import VoiceManager

                    vm = VoiceManager()
                    greet = await vm.synthesize_async("Oi. Entrei na call. Pode falar.")

                    async def on_utt(text: str, member: Any) -> None:
                        await adapter._handle_voice_utterance(text, member, message.guild)

                    status = await join_and_listen(
                        self,
                        message,
                        on_user_text=on_utt,
                        greeting_audio=str(greet) if greet else None,
                    )
                    await message.channel.send(status)
                    if greet:
                        Path(greet).unlink(missing_ok=True)
                    return

                inbound = InboundMessage(
                    text=content,
                    user_id=str(message.author.id),
                    channel_id=str(message.channel.id),
                    platform=PlatformId.DISCORD.value,
                    correlation_id=str(message.id),
                    metadata={
                        "guild_id": str(message.guild.id) if message.guild else None,
                        "in_voice_with_bot": adapter._bot_in_same_call(message),
                    },
                )

                try:
                    result = adapter._handler(inbound)
                    outbound = await result if hasattr(result, "__await__") else result
                    if not outbound:
                        return

                    # na call → só fala
                    if adapter._bot_in_same_call(message) and outbound.text:
                        from app.voice.manager import VoiceManager

                        vm = VoiceManager()
                        audio_path = await vm.synthesize_async(outbound.text)
                        if audio_path and message.guild:
                            played = await play_in_guild(message.guild, audio_path)
                            Path(audio_path).unlink(missing_ok=True)
                            if played:
                                return

                    # fora da call + pediu áudio → voice message nativa (não anexo solto)
                    if wants_audio(content) and outbound.text:
                        from app.voice.manager import VoiceManager

                        vm = VoiceManager()
                        audio_path = await vm.synthesize_async(outbound.text)
                        if audio_path:
                            ok = await send_native_voice_message(
                                message.channel, audio_path, fallback_text=""
                            )
                            Path(audio_path).unlink(missing_ok=True)
                            if ok:
                                return

                    if outbound.text:
                        await message.channel.send(outbound.text[:1900])
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

    async def _send_outbound(self, channel: Any, outbound: OutboundMessage) -> None:
        if outbound.text:
            await channel.send(outbound.text[:1900])

    async def stop(self) -> None:
        self._started = False
        if self._client is not None:
            try:
                await self._client.close()
            except Exception:
                logger.exception("close failed")
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
            "stt": stt_available(),
            "mode": self._mode,
        }
