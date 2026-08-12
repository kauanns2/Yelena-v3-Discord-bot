"""Ledger de evolução — registra adaptações graduais da Yelena."""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Any

from app.bridge.constants import ContinuityNamespace
from app.bridge.continuity.store import ContinuityStore


@dataclass(slots=True)
class EvolutionEvent:
    kind: str
    description: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source_module: str = ""
    payload: dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.5
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "kind": self.kind,
            "description": self.description,
            "source_module": self.source_module,
            "payload": self.payload,
            "confidence": self.confidence,
            "created_at": self.created_at,
        }


class EvolutionLedger:
    """Registra e consulta eventos de evolução.

    Não aplica mudanças sozinho nos módulos 1–16.
    Apenas guarda evidências para uso futuro / revisão.
    """

    def __init__(self, store: ContinuityStore) -> None:
        self._store = store
        self._buffer: list[EvolutionEvent] = []

    def record(
        self,
        kind: str,
        description: str,
        *,
        source_module: str = "",
        payload: dict[str, Any] | None = None,
        confidence: float = 0.5,
    ) -> EvolutionEvent:
        event = EvolutionEvent(
            kind=kind,
            description=description,
            source_module=source_module,
            payload=payload or {},
            confidence=confidence,
        )
        self._buffer.append(event)
        # persist
        key = event.id
        self._store.put(
            ContinuityNamespace.EVOLUTION,
            key,
            event.to_dict(),
            metadata={"kind": kind, "source_module": source_module},
        )
        return event

    def recent(self, n: int = 20) -> list[dict[str, Any]]:
        keys = self._store.list_keys(ContinuityNamespace.EVOLUTION)
        events: list[dict[str, Any]] = []
        for key in keys[-n:]:
            val = self._store.get(ContinuityNamespace.EVOLUTION, key)
            if isinstance(val, dict):
                events.append(val)
        events.sort(key=lambda e: e.get("created_at", 0))
        return events[-n:]

    def health(self) -> dict[str, Any]:
        return {
            "status": "healthy",
            "buffered": len(self._buffer),
            "stored": len(self._store.list_keys(ContinuityNamespace.EVOLUTION)),
        }
