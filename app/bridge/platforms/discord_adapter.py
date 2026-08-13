"""Adapter Discord — voz nativa no chat + call."""

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
from app.voice.call import is_join_request, is_leave_request, join_and_speak, leave_voice
from app.voice.native_message import send_native_voice_message

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

        if self._mode == "mention":
            return False

        if INTEREST_RE.search(content) and random.random() < 0.12:
            return True

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
                    "discord adapter online user=%s mode=%s",
                    str(self.user),
                    adapter._mode,
                )

            async def on_message(self, message: discord.Message) -> None:  # type: ignore[override]
                if message.author.bot:
                    return
                if adapter._handler is None:
                    return
                if not (message.content or "").strip():
                    return
                if not adapter._should_respond(message):
                    return

                content = message.content or ""

                # --- call / leave (antes do pipeline de chat) ---
                if is_leave_request(content) and NAME_RE.search(content):
                    text = await leave_voice(self, message.guild)
                    await message.channel.send(text)
                    return

                if is_join_request(content) and (NAME_RE.search(content) or True):
                    # sintetiza fala curta se bridge tiver voice via handler
                    inbound = InboundMessage(
                        text=content,
                        user_id=str(message.author.id),
                        channel_id=str(message.channel.id),
                        platform=PlatformId.DISCORD.value,
                        correlation_id=str(message.id),
                    )
                    try:
                        result = adapter._handler(inbound)
                        if hasattr(result, "__await__"):
                            outbound = await result  # type: ignore[misc]
                        else:
                            outbound = result
                    except Exception:
                        outbound = None

                    audio = getattr(outbound, "audio_path", None) if outbound else None
                    # se não gerou áudio no pedido de call, tenta texto curto
                    if not audio:
                        try:
                            from app.voice.manager import VoiceManager

                            vm = VoiceManager()
                            p = await vm.synthesize_async("Oi. Entrei na call.")
                            audio = str(p) if p else None
                        except Exception:
                            audio = None

                    status = await join_and_speak(self, message, audio)
                    await message.channel.send(status)
                    if audio:
                        try:
                            Path(audio).unlink(missing_ok=True)
                        except Exception:
                            pass
                    return

                inbound = InboundMessage(
                    text=content,
                    user_id=str(message.author.id),
                    channel_id=str(message.channel.id),
                    platform=PlatformId.DISCORD.value,
                    session_id=None,
                    correlation_id=str(message.id),
                    metadata={
                        "guild_id": str(message.guild.id) if message.guild else None,
                        "author_name": str(message.author),
                    },
                )

                try:
                    result = adapter._handler(inbound)
                    if hasattr(result, "__await__"):
                        outbound = await result  # type: ignore[misc]
                    else:
                        outbound = result  # type: ignore[assignment]
                    if not outbound:
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
                # só voz nativa — sem texto junto (igual mensagem de voz do app)
                ok = await send_native_voice_message(channel, audio, fallback_text=text)
                if not ok and text:
                    await channel.send(text)
            finally:
                try:
                    Path(audio).unlink(missing_ok=True)
                except Exception:
                    pass
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
            try:
                channel = await self._client.fetch_channel(int(message.channel_id))
            except Exception as exc:
                raise PlatformError(f"Channel not found: {message.channel_id}") from exc
        await self._send_outbound(channel, message)

    def health(self) -> dict[str, Any]:
        return {
            "platform": self.platform_id,
            "status": "online" if self._started else "offline",
            "token_configured": bool(self._token),
            "mode": self._mode,
        }
