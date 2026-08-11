"""Políticas de decay, consolidação e esquecimento."""

from __future__ import annotations

import time

from app.memory.constants import MemoryStatus, MemoryType
from app.memory.models.memory import Memory


def apply_decay(memory: Memory, now: float | None = None) -> Memory:
    now = now or time.time()
    dt = now - memory.updated_at
    if dt > 0:
        memory.decay(dt)
    return memory


def should_forget(memory: Memory) -> bool:
    if memory.status == MemoryStatus.FORGOTTEN:
        return False
    if memory.importance >= 0.8:
        return False
    if memory.strength < 0.05 and memory.access_count < 2:
        return True
    if memory.is_expired:
        return True
    return False


def should_consolidate(memory: Memory) -> bool:
    if memory.status != MemoryStatus.ACTIVE:
        return False
    if memory.access_count >= 5 and memory.importance >= 0.6:
        return True
    if memory.memory_type in {MemoryType.PREFERENCE, MemoryType.AUTOBIOGRAPHICAL}:
        return memory.access_count >= 2
    return False


def consolidate(memory: Memory) -> Memory:
    memory.status = MemoryStatus.CONSOLIDATED
    memory.strength = min(2.0, memory.strength + 0.2)
    memory.decay_rate *= 0.5
    memory.updated_at = time.time()
    memory.version += 1
    return memory


def forget(memory: Memory) -> Memory:
    memory.status = MemoryStatus.FORGOTTEN
    memory.strength = 0.0
    memory.updated_at = time.time()
    memory.version += 1
    return memory
