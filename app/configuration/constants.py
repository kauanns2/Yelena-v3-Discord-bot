"""Constantes do Configuration System."""

from enum import Enum


class Environment(str, Enum):
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class ReloadPolicy(str, Enum):
    HOT_RELOADABLE = "hot_reloadable"
    RESTART_REQUIRED = "restart_required"
    IMMUTABLE = "immutable"


class ConfigSourceType(str, Enum):
    DEFAULT = "default"
    FILE = "file"
    ENVIRONMENT = "environment"
    MEMORY = "memory"


# Precedência: maior número = maior prioridade
SOURCE_PRIORITY = {
    ConfigSourceType.DEFAULT: 10,
    ConfigSourceType.FILE: 20,
    ConfigSourceType.ENVIRONMENT: 30,
    ConfigSourceType.MEMORY: 40,
}

SECRET_MASK = "********"
