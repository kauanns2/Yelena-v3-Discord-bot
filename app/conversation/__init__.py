"""
Módulo 11 — Conversation & Dialogue Management System

Administra sessões, turnos, intenções, tópicos e ResponseSpecification.
NÃO é o modelo de linguagem. NÃO gera o texto final.
"""

from app.conversation.manager import ConversationManager
from app.conversation.models.session import ConversationSession
from app.conversation.errors import ConversationError

__all__ = ["ConversationManager", "ConversationSession", "ConversationError"]
