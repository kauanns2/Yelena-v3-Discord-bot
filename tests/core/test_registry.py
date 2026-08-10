"""Testes do ModuleRegistry."""

import pytest

from app.core.exceptions import RegistryError
from app.core.models.module import ModuleInfo
from app.core.registry import ModuleRegistry


def test_register_and_get():
    reg = ModuleRegistry()
    mod = ModuleInfo(id="memory", name="Memory System")
    reg.register(mod)
    assert reg.has("memory")
    assert reg.get("memory") is mod
    assert len(reg) == 1


def test_duplicate_register():
    reg = ModuleRegistry()
    mod = ModuleInfo(id="memory", name="Memory System")
    reg.register(mod)
    with pytest.raises(RegistryError):
        reg.register(ModuleInfo(id="memory", name="Dup"))


def test_unregister():
    reg = ModuleRegistry()
    reg.register(ModuleInfo(id="memory", name="Memory"))
    removed = reg.unregister("memory")
    assert removed.id == "memory"
    assert not reg.has("memory")


def test_require_missing():
    reg = ModuleRegistry()
    with pytest.raises(RegistryError):
        reg.require("nonexistent")
