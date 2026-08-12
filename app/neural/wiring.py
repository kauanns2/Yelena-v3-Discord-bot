"""Registro canônico dos módulos na Teia Neural.

Não executa lógica de domínio — só topologia.
"""

from __future__ import annotations

import logging
from typing import Any

from app.neural.constants import NodeType

logger = logging.getLogger(__name__)

# nome_nó → (module_id legível, conexões de saída)
CANONICAL_NODES: list[str] = [
    "configuration",
    "core",
    "runtime",
    "neural",
    "event_bus",
    "memory",
    "knowledge",
    "context",
    "emotion",
    "personality",
    "identity",
    "reasoning",
    "conversation",
    "language",
    "actions",
    "security",
    "observability",
    "bridge",
]

# arestas dirigidas (source → target). Peso 1.0 padrão.
CANONICAL_EDGES: list[tuple[str, str, float]] = [
    ("configuration", "runtime", 1.0),
    ("core", "runtime", 1.0),
    ("runtime", "neural", 1.0),
    ("runtime", "event_bus", 0.9),
    ("neural", "event_bus", 0.8),
    ("memory", "context", 1.0),
    ("knowledge", "context", 1.0),
    ("context", "emotion", 0.7),
    ("context", "reasoning", 0.9),
    ("emotion", "personality", 0.8),
    ("personality", "identity", 0.9),
    ("identity", "reasoning", 0.8),
    ("personality", "reasoning", 0.9),
    ("emotion", "reasoning", 0.7),
    ("reasoning", "conversation", 1.0),
    ("conversation", "language", 1.0),
    ("language", "bridge", 1.0),
    ("security", "actions", 1.0),
    ("security", "bridge", 0.9),
    ("observability", "runtime", 0.5),
    ("bridge", "runtime", 0.6),
    ("memory", "knowledge", 0.6),
]


def wire_canonical_topology(neural: Any) -> dict[str, int]:
    """Registra nós e arestas se ainda não existirem. Idempotente o bastante."""
    if neural is None:
        return {"nodes": 0, "edges": 0}

    nodes_added = 0
    edges_added = 0

    for name in CANONICAL_NODES:
        try:
            if hasattr(neural.topology, "get_node") and neural.topology.get_node(name):
                continue
        except Exception:
            pass
        try:
            neural.register_node(
                name=name,
                node_type=NodeType.MODULE,
                module_id=name,
                node_id=name,
                metadata={"canonical": True},
            )
            nodes_added += 1
        except Exception:
            # nó já existe ou topologia rejeitou — ok
            pass

    for src, tgt, weight in CANONICAL_EDGES:
        try:
            neural.connect(src, tgt, weight=weight, bidirectional=False, metadata={"canonical": True})
            edges_added += 1
        except Exception:
            pass

    logger.info(
        "neural topology wired nodes_added=%s edges_added=%s",
        nodes_added,
        edges_added,
    )
    return {"nodes": nodes_added, "edges": edges_added}
