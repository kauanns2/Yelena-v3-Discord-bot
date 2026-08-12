"""
Módulo 17 — Platform Bridge, Continuity & Evolution

Borda multi-plataforma, cofre de continuidade, evolução e resiliência.
Conecta canais externos (Discord e futuros bots) aos módulos 1–16
sem absorver a lógica cognitiva deles.
"""

from app.bridge.manager import BridgeManager
from app.bridge.errors import BridgeError

__all__ = ["BridgeManager", "BridgeError"]
