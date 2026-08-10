"""Propagação de sinais com TTL e proteção contra loops."""

from __future__ import annotations

import logging
from typing import Any, Callable

from app.neural.constants import SignalPriority
from app.neural.errors import LoopDetectedError, TTLExpiredError, PropagationError, NodeError
from app.neural.models.signal import Signal
from app.neural.topology import Topology
from app.neural.types import NodeId

logger = logging.getLogger(__name__)

SignalHandler = Callable[[Signal, NodeId], Any]


class SignalPropagator:
    """Propaga sinais pela topologia com controles de segurança."""

    def __init__(self, topology: Topology) -> None:
        self._topology = topology
        self._handlers: dict[NodeId, list[SignalHandler]] = {}
        self._metrics = {
            "signals_sent": 0,
            "signals_delivered": 0,
            "signals_expired": 0,
            "loops_blocked": 0,
            "propagation_errors": 0,
        }

    def register_handler(self, node_id: NodeId, handler: SignalHandler) -> None:
        self._handlers.setdefault(node_id, []).append(handler)

    def unregister_handlers(self, node_id: NodeId) -> None:
        self._handlers.pop(node_id, None)

    def propagate(self, signal: Signal) -> list[NodeId]:
        """Propaga o sinal e retorna nós que o receberam."""
        self._metrics["signals_sent"] += 1
        delivered: list[NodeId] = []

        if signal.is_expired:
            self._metrics["signals_expired"] += 1
            raise TTLExpiredError(
                f"Signal expired: {signal.id}",
                context={"signal_id": signal.id},
            )

        # destino explícito
        if signal.target_id:
            if signal.target_id in signal.path:
                self._metrics["loops_blocked"] += 1
                raise LoopDetectedError(
                    f"Loop detected: {signal.target_id} already in path",
                    context={"path": signal.path, "target": signal.target_id},
                )
            self._deliver(signal, signal.target_id)
            delivered.append(signal.target_id)
            return delivered

        # propagação pelos vizinhos do source
        if not signal.source_id:
            raise PropagationError("Signal requires source_id for topology propagation")

        visited = set(signal.path)
        queue: list[tuple[NodeId, Signal]] = []

        for neighbor in self._topology.neighbors(signal.source_id):
            if neighbor not in visited:
                queue.append((neighbor, signal))

        while queue:
            node_id, current = queue.pop(0)

            if current.is_expired:
                self._metrics["signals_expired"] += 1
                continue

            if node_id in current.path:
                self._metrics["loops_blocked"] += 1
                continue

            if not current.can_propagate:
                continue

            # clonar hop state
            hop_signal = Signal(
                id=current.id,
                signal_type=current.signal_type,
                source_id=current.source_id,
                target_id=node_id,
                payload=current.payload,
                priority=current.priority,
                ttl=current.ttl,
                max_hops=current.max_hops,
                hops=current.hops,
                path=list(current.path),
                correlation_id=current.correlation_id,
                created_at=current.created_at,
                metadata=dict(current.metadata),
            )
            hop_signal.hop(node_id)

            try:
                self._deliver(hop_signal, node_id)
                delivered.append(node_id)
            except Exception:
                self._metrics["propagation_errors"] += 1
                logger.exception("delivery failed", extra={"node_id": node_id})
                continue

            # continuar propagação se ainda pode
            if hop_signal.can_propagate:
                for next_neighbor in self._topology.neighbors(node_id):
                    if next_neighbor not in hop_signal.path:
                        queue.append((next_neighbor, hop_signal))

        return delivered

    def _deliver(self, signal: Signal, node_id: NodeId) -> None:
        node = self._topology.get_node(node_id)
        if node is None or not node.is_active:
            raise NodeError(f"Cannot deliver to inactive/missing node: {node_id}")

        handlers = self._handlers.get(node_id, [])
        for handler in handlers:
            handler(signal, node_id)

        self._metrics["signals_delivered"] += 1
        logger.debug(
            "signal delivered",
            extra={"signal_id": signal.id, "node_id": node_id, "hops": signal.hops},
        )

    @property
    def metrics(self) -> dict[str, int]:
        return dict(self._metrics)
