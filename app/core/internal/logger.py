"""Adapter de logging do Core."""

from __future__ import annotations

import logging
import sys
from typing import Any


def setup_core_logging(level: int = logging.INFO) -> None:
    """Configura logging básico estruturado para o Core."""
    root = logging.getLogger("app")
    if root.handlers:
        return

    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    root.addHandler(handler)
    root.setLevel(level)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
