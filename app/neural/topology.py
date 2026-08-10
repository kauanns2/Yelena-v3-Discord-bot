"""Topologia da Teia — grafo de nós e arestas."""

from __future__ import annotations

import logging
from collections import defaultdict
from typing import Iterator

from app.neural.constants import NodeStatus
from app.neural.errors import NodeError, EdgeError, TopologyError
from app.neural.models.node import Node
from app.neural.models.edge import Edge
from app.neural.types import NodeId, EdgeId

logger = logging.getLogger(__name__)


class Topology:
    """Representa a estrutura de conexões da Neural Web."""

    def __init__(self) -> None:
        self._nodes: dict[NodeId, Node] = {}
        self._edges: dict[EdgeId, Edge] = {}
        self._outbound: dict[NodeId, list[EdgeId]] = defaultdict(list)
        self._inbound: dict[NodeId, list[EdgeId]] = defaultdict(list)

    # --- Nodes ---

    def add_node(self, node: Node) -> Node:
        if node.id in self._nodes:
            raise NodeError(f"Node already exists: {node.id}", context={"node_id": node.id})
        self._nodes[node.id] = node
        logger.debug("node added", extra={"node_id": node.id})
        return node

    def remove_node(self, node_id: NodeId) -> Node:
        if node_id not in self._nodes:
            raise NodeError(f"Node not found: {node_id}", context={"node_id": node_id})

        # remover arestas conectadas
        edge_ids = list(self._outbound.get(node_id, [])) + list(self._inbound.get(node_id, []))
        for eid in set(edge_ids):
            self._edges.pop(eid, None)

        self._outbound.pop(node_id, None)
        self._inbound.pop(node_id, None)

        # limpar referências em outras listas
        for edges in self._outbound.values():
            edges[:] = [e for e in edges if e in self._edges]
        for edges in self._inbound.values():
            edges[:] = [e for e in edges if e in self._edges]

        node = self._nodes.pop(node_id)
        logger.debug("node removed", extra={"node_id": node_id})
        return node

    def get_node(self, node_id: NodeId) -> Node | None:
        return self._nodes.get(node_id)

    def require_node(self, node_id: NodeId) -> Node:
        node = self.get_node(node_id)
        if node is None:
            raise NodeError(f"Node not found: {node_id}", context={"node_id": node_id})
        return node

    def list_nodes(self) -> list[Node]:
        return list(self._nodes.values())

    def active_nodes(self) -> list[Node]:
        return [n for n in self._nodes.values() if n.status == NodeStatus.ACTIVE]

    # --- Edges ---

    def add_edge(self, edge: Edge) -> Edge:
        if edge.source_id not in self._nodes:
            raise EdgeError(
                f"Source node not found: {edge.source_id}",
                context={"source_id": edge.source_id},
            )
        if edge.target_id not in self._nodes:
            raise EdgeError(
                f"Target node not found: {edge.target_id}",
                context={"target_id": edge.target_id},
            )
        if edge.id in self._edges:
            raise EdgeError(f"Edge already exists: {edge.id}", context={"edge_id": edge.id})

        self._edges[edge.id] = edge
        self._outbound[edge.source_id].append(edge.id)
        self._inbound[edge.target_id].append(edge.id)

        if edge.bidirectional:
            # aresta lógica reversa (mesmo id + sufixo)
            reverse_id = f"{edge.id}:reverse"
            if reverse_id not in self._edges:
                reverse = Edge(
                    id=reverse_id,
                    source_id=edge.target_id,
                    target_id=edge.source_id,
                    edge_type=edge.edge_type,
                    weight=edge.weight,
                    bidirectional=False,
                    metadata={**edge.metadata, "reverse_of": edge.id},
                )
                self._edges[reverse.id] = reverse
                self._outbound[reverse.source_id].append(reverse.id)
                self._inbound[reverse.target_id].append(reverse.id)

        logger.debug(
            "edge added",
            extra={"edge_id": edge.id, "source": edge.source_id, "target": edge.target_id},
        )
        return edge

    def remove_edge(self, edge_id: EdgeId) -> Edge:
        if edge_id not in self._edges:
            raise EdgeError(f"Edge not found: {edge_id}", context={"edge_id": edge_id})
        edge = self._edges.pop(edge_id)
        if edge_id in self._outbound.get(edge.source_id, []):
            self._outbound[edge.source_id].remove(edge_id)
        if edge_id in self._inbound.get(edge.target_id, []):
            self._inbound[edge.target_id].remove(edge_id)
        return edge

    def neighbors(self, node_id: NodeId) -> list[NodeId]:
        result: list[NodeId] = []
        for eid in self._outbound.get(node_id, []):
            edge = self._edges.get(eid)
            if edge:
                result.append(edge.target_id)
        return result

    def edges_from(self, node_id: NodeId) -> list[Edge]:
        return [
            self._edges[eid]
            for eid in self._outbound.get(node_id, [])
            if eid in self._edges
        ]

    def list_edges(self) -> list[Edge]:
        return list(self._edges.values())

    def __len__(self) -> int:
        return len(self._nodes)

    def stats(self) -> dict:
        return {
            "nodes": len(self._nodes),
            "edges": len(self._edges),
            "active_nodes": len(self.active_nodes()),
        }
