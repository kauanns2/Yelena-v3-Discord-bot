"""Store abstrato e implementação em memória."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterator

from app.memory.errors import MemoryNotFoundError, MemoryStoreError
from app.memory.models.memory import Memory
from app.memory.types import MemoryId


class MemoryStore(ABC):
    @abstractmethod
    def save(self, memory: Memory) -> Memory: ...

    @abstractmethod
    def get(self, memory_id: MemoryId) -> Memory | None: ...

    @abstractmethod
    def delete(self, memory_id: MemoryId) -> bool: ...

    @abstractmethod
    def list_all(self) -> list[Memory]: ...

    @abstractmethod
    def __len__(self) -> int: ...


class InMemoryStore(MemoryStore):
    """Store volátil para desenvolvimento e testes."""

    def __init__(self) -> None:
        self._data: dict[MemoryId, Memory] = {}

    def save(self, memory: Memory) -> Memory:
        self._data[memory.id] = memory
        return memory

    def get(self, memory_id: MemoryId) -> Memory | None:
        return self._data.get(memory_id)

    def require(self, memory_id: MemoryId) -> Memory:
        mem = self.get(memory_id)
        if mem is None:
            raise MemoryNotFoundError(
                f"Memory not found: {memory_id}",
                context={"memory_id": memory_id},
            )
        return mem

    def delete(self, memory_id: MemoryId) -> bool:
        return self._data.pop(memory_id, None) is not None

    def list_all(self) -> list[Memory]:
        return list(self._data.values())

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self) -> Iterator[Memory]:
        return iter(self._data.values())
