"""Testes de topologia."""

import pytest

from app.neural.errors import NodeError, EdgeError
from app.neural.models.node import Node
from app.neural.models.edge import Edge
from app.neural.topology import Topology
from app.neural.constants import NodeType


def test_add_and_get_node():
    topo = Topology()
    node = Node(id="memory", name="Memory", node_type=NodeType.MODULE)
    topo.add_node(node)
    assert topo.get_node("memory") is node
    assert len(topo) == 1


def test_duplicate_node():
    topo = Topology()
    topo.add_node(Node(id="a", name="A"))
    with pytest.raises(NodeError):
        topo.add_node(Node(id="a", name="A2"))


def test_edge_and_neighbors():
    topo = Topology()
    topo.add_node(Node(id="a", name="A"))
    topo.add_node(Node(id="b", name="B"))
    topo.add_edge(Edge(source_id="a", target_id="b"))
    assert topo.neighbors("a") == ["b"]


def test_self_edge_forbidden():
    with pytest.raises(ValueError):
        Edge(source_id="a", target_id="a")
