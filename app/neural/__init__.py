"""
Módulo 3 — Neural Web / Teia Neural

Infraestrutura de relacionamento e propagação de sinais entre componentes.
Não é um God Object. Não contém lógica de domínio dos outros módulos.
"""

from app.neural.manager import NeuralWebManager
from app.neural.models.node import Node
from app.neural.models.edge import Edge
from app.neural.models.signal import Signal
from app.neural.errors import NeuralError

__all__ = [
    "NeuralWebManager",
    "Node",
    "Edge",
    "Signal",
    "NeuralError",
]
