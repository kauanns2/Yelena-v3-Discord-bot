"""Testes do DependencyResolver."""

import pytest

from app.core.dependency import DependencyResolver
from app.core.exceptions import DependencyError
from app.core.models.module import ModuleInfo, ModuleDependency
from app.core.registry import ModuleRegistry


def _reg_with(*modules: ModuleInfo) -> ModuleRegistry:
    reg = ModuleRegistry()
    for m in modules:
        reg.register(m)
    return reg


def test_simple_order():
    reg = _reg_with(
        ModuleInfo(id="core", name="Core"),
        ModuleInfo(
            id="config",
            name="Config",
            dependencies=[ModuleDependency(module_id="core")],
        ),
        ModuleInfo(
            id="memory",
            name="Memory",
            dependencies=[ModuleDependency(module_id="config")],
        ),
    )
    resolver = DependencyResolver(reg)
    order = resolver.resolve_order()
    assert order.index("core") < order.index("config")
    assert order.index("config") < order.index("memory")


def test_missing_dependency():
    reg = _reg_with(
        ModuleInfo(
            id="memory",
            name="Memory",
            dependencies=[ModuleDependency(module_id="missing")],
        )
    )
    resolver = DependencyResolver(reg)
    with pytest.raises(DependencyError):
        resolver.validate()


def test_cycle_detection():
    reg = _reg_with(
        ModuleInfo(
            id="a",
            name="A",
            dependencies=[ModuleDependency(module_id="b")],
        ),
        ModuleInfo(
            id="b",
            name="B",
            dependencies=[ModuleDependency(module_id="a")],
        ),
    )
    resolver = DependencyResolver(reg)
    cycles = resolver.detect_cycles()
    assert len(cycles) > 0
