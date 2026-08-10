"""
Módulo 1 — Core & Kernel

Fundação operacional da Yelena V3.
Fornece: lifecycle, registry, dependency management,
state, health, loader, contratos e bootstrap.

Não contém lógica de personalidade, memória, emoção, Discord, IA ou raciocínio.
"""

from app.core.version import CORE_VERSION, YELENA_VERSION
from app.core.constants import LifecycleState, HealthStatus
from app.core.exceptions import CoreError

__all__ = [
    "CORE_VERSION",
    "YELENA_VERSION",
    "LifecycleState",
    "HealthStatus",
    "CoreError",
]
