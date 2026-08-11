"""
Camada de integração (borda).

Mantém o Core/Runtime independentes de Discord.
O intermediário existente usa o Gateway ou a HTTP API.
"""

from app.integration.gateway import YelenaGateway
from app.integration.contracts import ProcessMessageRequest, ProcessMessageResponse

__all__ = [
    "YelenaGateway",
    "ProcessMessageRequest",
    "ProcessMessageResponse",
]
