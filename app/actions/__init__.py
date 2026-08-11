"""
Módulo 13 — Action & Tool Execution System

Transforma decisões executáveis em ações controladas via ferramentas.
Pensar ≠ Executar. Autorização e risco antes da execução.
"""

from app.actions.manager import ActionManager
from app.actions.models.tool import Tool
from app.actions.models.result import ActionResult
from app.actions.errors import ActionError

__all__ = ["ActionManager", "Tool", "ActionResult", "ActionError"]
