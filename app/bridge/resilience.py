"""Fronteira de resiliência — reduz falhas em cascata dos módulos 1–16."""

from __future__ import annotations

import logging
from typing import Any, Callable, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


class ResilienceBoundary:
    """Executa operações com fallback e registro de erro."""

    def __init__(self) -> None:
        self._errors: list[dict[str, Any]] = []
        self._max_errors = 200

    def run(
        self,
        label: str,
        fn: Callable[[], T],
        *,
        fallback: T | None = None,
        default_factory: Callable[[], T] | None = None,
    ) -> T | None:
        try:
            return fn()
        except Exception as exc:
            self._record(label, str(exc))
            logger.exception("resilience caught error", extra={"label": label})
            if default_factory is not None:
                try:
                    return default_factory()
                except Exception:
                    return fallback
            return fallback

    def _record(self, label: str, error: str) -> None:
        import time

        self._errors.append({"label": label, "error": error, "at": time.time()})
        if len(self._errors) > self._max_errors:
            self._errors = self._errors[-self._max_errors :]

    def recent_errors(self, n: int = 20) -> list[dict[str, Any]]:
        return self._errors[-n:]

    def health(self) -> dict[str, Any]:
        return {
            "status": "healthy",
            "recent_errors": len(self._errors),
        }
