"""Neural Web Manager — coordenação da Teia."""

from __future__ import annotations

import logging
from typing import Any

from app.neural.constants import NodeType, NodeStatus, DEFAULT_MAX_HOPS, DEFAULT_TTL
from app.neural.models.node import Node
from app.neural.models.edge import Edge
from app.neural.models.signal import Signal
from app.neural.propagator import SignalPropagator, SignalHandler
from app.neural.topology import Topology
from app.neural.types import NodeId

logger = logging.getLogger(__name__)


class NeuralWebManager:
    """Gerencia topologia, nós, arestas e propagação de sinais.

    Não contém lógica de memória, emoção, reasoning, etc.
    Apenas infraestrutura de conexão.
    """

    def __init__(
        self,
        max_hops: int = DEFAULT_MAX_HOPS,
        default_ttl: float = DEFAULT_TTL,
    ) -> None:
        self.topology = Topology()
        self.propagator = SignalPropagator(self.topology)
        self.max_hops = max_hops
        self.default_ttl = default_ttl
        self._started = False

    @property
    def is_started(self) -> bool:
        return self._started

    def start(self) -> None:
        self._started = True
        logger.info("neural web started", extra=self.topology.stats())

    def stop(self) -> None:
        self._started = False
        logger.info("neural web stopped")

    # --- Nodes ---

    def register_node(
        self,
        name: str,
        node_type: NodeType = NodeType.MODULE,
        module_id: str | None = None,
        node_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Node:
        node = Node(
            id=node_id or name,
            name=name,
            node_type=node_type,
            module_id=module_id or name,
            metadata=metadata or {},
        )
        return self.topology.add_node(node)

    def unregister_node(self, node_id: NodeId) -> None:
        self.propagator.unregister_handlers(node_id)
        self.topology.remove_node(node_id)

    def connect(
        self,
        source_id: NodeId,
        target_id: NodeId,
        weight: float = 1.0,
        bidirectional: bool = False,
        metadata: dict[str, Any] | None = None,
    ) -> Edge:
        edge = Edge(
            source_id=source_id,
            target_id=target_id,
            weight=weight,
            bidirectional=bidirectional,
            metadata=metadata or {},
        )
        return self.topology.add_edge(edge)

    def on_signal(self, node_id: NodeId, handler: SignalHandler) -> None:
        self.propagator.register_handler(node_id, handler)

    def emit(self, signal: Signal) -> list[NodeId]:
        if signal.max_hops == DEFAULT_MAX_HOPS and self.max_hops != DEFAULT_MAX_HOPS:
            signal.max_hops = self.max_hops
        if signal.ttl == DEFAULT_TTL and self.default_ttl != DEFAULT_TTL:
            signal.ttl = self.default_ttl
        return self.propagator.propagate(signal)

    def health(self) -> dict[str, Any]:
        stats = self.topology.stats()
        return {
            "status": "healthy" if self._started else "stopped",
            "started": self._started,
            **stats,
            "metrics": self.propagator.metrics,
        }

    def snapshot(self) -> dict[str, Any]:
        return {
            "nodes": [n.to_dict() for n in self.topology.list_nodes()],
            "edges": [e.to_dict() for e in self.topology.list_edges()],
            "health": self.health(),
        }
