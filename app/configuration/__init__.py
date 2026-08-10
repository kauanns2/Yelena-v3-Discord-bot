"""
Módulo 2 — Configuration

Centraliza, valida e fornece configuração tipada para toda a Yelena.
Nenhum módulo futuro deve acessar os.environ ou arquivos .env diretamente.
"""

from app.configuration.manager import ConfigurationManager
from app.configuration.models.config import YelenaConfig
from app.configuration.errors import ConfigurationError, ConfigValidationError, SecretError

__all__ = [
    "ConfigurationManager",
    "YelenaConfig",
    "ConfigurationError",
    "ConfigValidationError",
    "SecretError",
]
