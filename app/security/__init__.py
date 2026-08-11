"""
Módulo 14 — Security & Authorization System

Autoridade independente de segurança da Yelena.
Nenhum módulo pode simplesmente declarar "esta ação é permitida".
"""

from app.security.manager import SecurityManager
from app.security.gate import SecurityGate
from app.security.errors import SecurityError

__all__ = ["SecurityManager", "SecurityGate", "SecurityError"]
