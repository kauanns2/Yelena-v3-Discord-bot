"""Testes do Memory Manager."""

import pytest

from app.memory import MemoryManager
from app.memory.constants import MemoryType, MemoryStatus
from app.memory.models.query import MemoryQuery
from app.memory.errors import MemoryValidationError, MemoryNotFoundError


def test_create_and_get():
    mm = MemoryManager()
    mm.start()
    mem = mm.create("Olá mundo", memory_type=MemoryType.EPISODIC)
    assert mem.id
    assert mm.get(mem.id) is not None


def test_empty_content_fails():
    mm = MemoryManager()
    with pytest.raises(MemoryValidationError):
        mm.create("   ")


def test_recall_text():
    mm = MemoryManager()
    mm.create("Usuário preocupado com o projeto Yelena", tags=["projeto"])
    mm.create("Gosta de café", tags=["preferencia"])
    result = mm.recall_text("projeto")
    assert result.total >= 1
    assert any("projeto" in m.content.lower() for m in result.memories)


def test_reinforce():
    mm = MemoryManager()
    mem = mm.create("teste", importance=0.5)
    old_strength = mem.strength
    updated = mm.reinforce(mem.id, 0.2)
    assert updated.strength > old_strength


def test_forget():
    mm = MemoryManager()
    mem = mm.create("temporário")
    forgotten = mm.forget(mem.id)
    assert forgotten.status == MemoryStatus.FORGOTTEN


def test_not_found():
    mm = MemoryManager()
    with pytest.raises(MemoryNotFoundError):
        mm.reinforce("nonexistent")
