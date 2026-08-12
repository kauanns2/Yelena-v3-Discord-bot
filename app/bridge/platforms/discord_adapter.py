"""Adapter Discord — fino. Não contém lógica cognitiva."""

from __future__ import annotations

import logging
import os
from typing import Any

from app.bridge.constants import PlatformId
from app.bridge.errors import PlatformError
from app.bridge.platforms.base import (
    InboundMessage,
    MessageHandler,
    OutboundMessage,
    PlatformAdapter,
)

logger = logging.getLogger(__name__)


class DiscordAdapter(PlatformAdapter):
    """Conecta ao Discord e encaminha mensagens ao handler do Bridge."""

    def __init__(self, token: str | None = None) -> None:
        self._token = token or os.getenv("DISCORD_TOKEN", "").strip()
        self._handler: MessageHandler | None = None
        self._client: Any = None
        self._started = False
        self._task: Any = None

    @property
    def platform_id(self) -> str:
        return PlatformId.DISCORD.value

    def set_handler(self, handler: MessageHandler) -> None:
        self._handler = handler

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

        adapter = self

        class YelenaClient(discord.Client):
            async def on_ready(self) -> None:  # type: ignore[override]
                adapter._started = True
                logger.info(
                    "discord adapter online user=%s",
                    str(self.user),
                )

            async def on_message(self, message: discord.Message) -> None:  # type: ignore[override]
                if message.author.bot:
                    return
                if adapter._handler is None:
                    return

                # session_id fica None: Runtime/Conversation cria e o Bridge mapeia
                inbound = InboundMessage(
                    text=message.content or "",
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
                if not inbound.text.strip():
                    return

                try:
                    result = adapter._handler(inbound)
                    if hasattr(result, "__await__"):
                        outbound = await result  # type: ignore[misc]
                    else:
                        outbound = result  # type: ignore[assignment]
                    if outbound and outbound.text:
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
        logger.info("discord adapter starting")

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
        await channel.send(message.text[:1900])

    def health(self) -> dict[str, Any]:
        return {
            "platform": self.platform_id,
            "status": "online" if self._started else "offline",
            "token_configured": bool(self._token),
        }
