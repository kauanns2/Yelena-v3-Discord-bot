"""Resolução de dependências com detecção de ciclos."""

from __future__ import annotations

import logging
from collections import defaultdict, deque

from app.core.exceptions import DependencyError
from app.core.models.module import ModuleInfo, ModuleDependency
from app.core.registry import ModuleRegistry
from app.core.types import ModuleId

logger = logging.getLogger(__name__)


class DependencyResolver:
    """Constrói grafo de dependências e resolve ordem de inicialização."""

    def __init__(self, registry: ModuleRegistry) -> None:
        self._registry = registry

    def build_graph(self) -> dict[ModuleId, list[ModuleId]]:
        """Grafo: module_id -> lista de dependências obrigatórias."""
        graph: dict[ModuleId, list[ModuleId]] = {}
        for module in self._registry:
            deps = [d.module_id for d in module.dependencies]
            graph[module.id] = deps
        return graph

    def detect_cycles(self) -> list[list[ModuleId]]:
        """Detecta ciclos no grafo de dependências."""
        graph = self.build_graph()
        visited: set[ModuleId] = set()
        stack: set[ModuleId] = set()
        cycles: list[list[ModuleId]] = []
        path: list[ModuleId] = []

        def dfs(node: ModuleId) -> None:
            if node in stack:
                cycle_start = path.index(node)
                cycles.append(path[cycle_start:] + [node])
                return
            if node in visited:
                return
            visited.add(node)
            stack.add(node)
            path.append(node)
            for dep in graph.get(node, []):
                dfs(dep)
            path.pop()
            stack.discard(node)

        for node in graph:
            dfs(node)
        return cycles

    def validate(self) -> None:
        """Valida dependências: existência e ciclos."""
        for module in self._registry:
            for dep in module.dependencies:
                if not self._registry.has(dep.module_id):
                    raise DependencyError(
                        f"Missing required dependency: {module.id} -> {dep.module_id}",
                        context={
                            "module_id": module.id,
                            "dependency": dep.module_id,
                            "optional": False,
                        },
                    )
            for dep in module.optional_dependencies:
                if not self._registry.has(dep.module_id):
                    logger.warning(
                        "optional dependency missing",
                        extra={
                            "module_id": module.id,
                            "dependency": dep.module_id,
                        },
                    )

        cycles = self.detect_cycles()
        if cycles:
            raise DependencyError(
                f"Dependency cycles detected: {cycles}",
                context={"cycles": cycles},
            )

    def resolve_order(self) -> list[ModuleId]:
        """Retorna ordem de inicialização (topological sort)."""
        self.validate()
        graph = self.build_graph()

        in_degree: dict[ModuleId, int] = defaultdict(int)
        for node in graph:
            in_degree.setdefault(node, 0)
            for dep in graph[node]:
                in_degree[node] += 1
                in_degree.setdefault(dep, 0)

        # Kahn: nós sem dependências primeiro
        queue: deque[ModuleId] = deque()
        for node, degree in in_degree.items():
            if degree == 0 or (node in graph and len(graph[node]) == 0):
                # recalcular corretamente
                pass

        # Rebuild in-degree properly: edge A->B means A depends on B
        # so B must start before A. in_degree[A] = number of deps of A
        in_degree = {node: len(deps) for node, deps in graph.items()}
        dependents: dict[ModuleId, list[ModuleId]] = defaultdict(list)
        for node, deps in graph.items():
            for dep in deps:
                dependents[dep].append(node)

        queue = deque([n for n, d in in_degree.items() if d == 0])
        order: list[ModuleId] = []

        while queue:
            node = queue.popleft()
            order.append(node)
            for dependent in dependents[node]:
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)

        if len(order) != len(graph):
            raise DependencyError(
                "Could not resolve full dependency order (possible cycle)",
                context={"partial_order": order},
            )

        # Respeitar prioridade entre nós sem dependência relativa
        modules_by_id = {m.id: m for m in self._registry}
        order.sort(key=lambda mid: (
            modules_by_id[mid].priority.value if mid in modules_by_id else 50,
            mid,
        ))

        # Re-validar ordem topológica após sort por prioridade
        # Sort estável por prioridade pode quebrar topo — fazer sort só entre independentes
        # Para simplicidade e correção, retornar ordem topológica pura
        # e deixar priority como desempate no Kahn

        return self._topo_with_priority()

    def _topo_with_priority(self) -> list[ModuleId]:
        graph = self.build_graph()
        modules_by_id = {m.id: m for m in self._registry}

        in_degree = {node: len(deps) for node, deps in graph.items()}
        dependents: dict[ModuleId, list[ModuleId]] = defaultdict(list)
        for node, deps in graph.items():
            for dep in deps:
                dependents[dep].append(node)

        available = [n for n, d in in_degree.items() if d == 0]
        available.sort(key=lambda mid: (
            modules_by_id[mid].priority.value if mid in modules_by_id else 50,
            mid,
        ))

        order: list[ModuleId] = []
        while available:
            node = available.pop(0)
            order.append(node)
            for dependent in dependents[node]:
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    available.append(dependent)
                    available.sort(key=lambda mid: (
                        modules_by_id[mid].priority.value if mid in modules_by_id else 50,
                        mid,
                    ))

        if len(order) != len(graph):
            raise DependencyError(
                "Could not resolve full dependency order",
                context={"partial_order": order},
            )
        return order

    def shutdown_order(self) -> list[ModuleId]:
        """Ordem de shutdown = inversa da inicialização."""
        return list(reversed(self.resolve_order()))
