"""
Módulo 16 — System Integration, Orchestration & Runtime Layer

Coordena lifecycle, composição e pipeline da Yelena.
Não absorve responsabilidades dos outros módulos.
"""

from app.runtime.runtime import YelenaRuntime
from app.runtime.errors import RuntimeError

__all__ = ["YelenaRuntime", "RuntimeError"]
