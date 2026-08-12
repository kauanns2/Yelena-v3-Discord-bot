"""Bridge Manager — Módulo 17."""

from __future__ import annotations

import logging
import os
from typing import Any, Callable

from app.bridge.constants import ContinuityNamespace
from app.bridge.continuity.store import ContinuityStore
from app.bridge.evolution.ledger import EvolutionLedger
from app.bridge.platforms.base import InboundMessage, OutboundMessage
from app.bridge.platforms.discord_adapter import DiscordAdapter
from app.bridge.platforms.registry import PlatformRegistry
from app.bridge.resilience import ResilienceBoundary

logger = logging.getLogger(__name__)


class BridgeManager:
    """Ponto central do Módulo 17."""

    def __init__(self, process_fn: Callable[..., Any] | None = None) -> None:
        self.platforms = PlatformRegistry()
        self.continuity = ContinuityStore()
        self.evolution = EvolutionLedger(self.continuity)
        self.resilience = ResilienceBoundary()
        self._process_fn = process_fn
        self._started = False
        self._session_map: dict[str, str] = {}

    def set_process_fn(self, fn: Callable[..., Any]) -> None:
        self._process_fn = fn

    @property
    def is_started(self) -> bool:
        return self._started

    def start(self) -> None:
        self._started = True
        stored = self.continuity.get(ContinuityNamespace.SESSION, "map", default={})
        if isinstance(stored, dict):
            self._session_map.update({str(k): str(v) for k, v in stored.items()})
        logger.info(
            "bridge system started platforms=%s",
            self.platforms.list_ids(),
        )

    def stop(self) -> None:
        self._started = False
        try:
            self.continuity.put(ContinuityNamespace.SESSION, "map", dict(self._session_map))
        except Exception:
            logger.exception("failed to persist session map")

    def register_discord(self, token: str | None = None) -> DiscordAdapter:
        adapter = DiscordAdapter(token=token)
        adapter.set_handler(self.handle_inbound)
        self.platforms.register(adapter)
        return adapter

    def handle_inbound(self, inbound: InboundMessage) -> OutboundMessage:
        def _process() -> OutboundMessage:
            if self._process_fn is None:
                return OutboundMessage(
                    text="Sistema ainda não está pronto para conversar.",
                    channel_id=inbound.channel_id,
                    user_id=inbound.user_id,
                )

            session_key = f"{inbound.platform}:{inbound.channel_id}:{inbound.user_id}"
            # só reutiliza session_id se já mapeada pelo Bridge (UUID real do Runtime)
            session_id = self._session_map.get(session_key)
            if inbound.session_id and inbound.session_id in self._session_map.values():
                session_id = inbound.session_id

            result = self._process_fn(
                inbound.text,
                user_id=f"{inbound.platform}:{inbound.user_id}",
                session_id=session_id,
                channel=inbound.platform,
                correlation_id=inbound.correlation_id or inbound.id,
            )

            text = getattr(result, "text", None) or str(result)
            new_session = getattr(result, "session_id", None)
            if new_session:
                self._session_map[session_key] = str(new_session)
                try:
                    self.continuity.put(
                        ContinuityNamespace.SESSION,
                        session_key,
                        str(new_session),
                        metadata={
                            "platform": inbound.platform,
                            "user_id": inbound.user_id,
                        },
                    )
                except Exception:
                    logger.exception("continuity session put failed")

            try:
                complexity = getattr(result, "complexity", None)
                complexity_val = (
                    complexity.value if hasattr(complexity, "value") else str(complexity or "")
                )
                self.evolution.record(
                    kind="interaction",
                    description=f"message via {inbound.platform}",
                    source_module="bridge",
                    payload={
                        "platform": inbound.platform,
                        "user_id": inbound.user_id,
                        "complexity": complexity_val,
                    },
                    confidence=float(getattr(result, "confidence", 0.5) or 0.5),
                )
            except Exception:
                logger.exception("evolution record failed")

            return OutboundMessage(
                text=text,
                channel_id=inbound.channel_id,
                user_id=inbound.user_id,
                reply_to=inbound.id,
            )

        try:
            return _process()
        except Exception:
            logger.exception(
                "bridge handle_inbound failed platform=%s user=%s",
                inbound.platform,
                inbound.user_id,
            )
            return OutboundMessage(
                text="Algo deu errado por aqui. Pode repetir?",
                channel_id=inbound.channel_id,
                user_id=inbound.user_id,
            )

    def deposit(
        self,
        namespace: str | ContinuityNamespace,
        key: str,
        value: Any,
        **metadata: Any,
    ) -> None:
        self.continuity.put(namespace, key, value, metadata=metadata or None)

    def recall(
        self,
        namespace: str | ContinuityNamespace,
        key: str,
        default: Any = None,
    ) -> Any:
        return self.continuity.get(namespace, key, default=default)

    def health(self) -> dict[str, Any]:
        platforms = {
            pid: (self.platforms.get(pid).health() if self.platforms.get(pid) else {})
            for pid in self.platforms.list_ids()
        }
        return {
            "status": "healthy" if self._started else "stopped",
            "platforms": platforms,
            "continuity": self.continuity.health(),
            "evolution": self.evolution.health(),
            "resilience": self.resilience.health(),
        }

    @staticmethod
    def discord_token_configured() -> bool:
        return bool(os.getenv("DISCORD_TOKEN", "").strip())
