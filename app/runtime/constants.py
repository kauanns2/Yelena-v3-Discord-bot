"""Constantes do Runtime."""

from enum import Enum


class RuntimeState(str, Enum):
    CREATED = "created"
    STARTING = "starting"
    READY = "ready"
    DEGRADED = "degraded"
    STOPPING = "stopping"
    STOPPED = "stopped"


class Complexity(str, Enum):
    TRIVIAL = "trivial"      # oi, tchau
    SIMPLE = "simple"
    NORMAL = "normal"
    COMPLEX = "complex"
    CRITICAL = "critical"   # ação perigosa
