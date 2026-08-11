"""
Módulo 15 — Observability, Monitoring & Diagnostics System

Métricas, logs estruturados, tracing, health e diagnóstico.
Não é Memory. Não é Security Audit. Não decide autonomamente.
"""

from app.observability.manager import ObservabilityManager
from app.observability.errors import ObservabilityError

__all__ = ["ObservabilityManager", "ObservabilityError"]
