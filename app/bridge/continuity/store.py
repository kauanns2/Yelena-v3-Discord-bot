"""Armazenamento durável de snapshots para uso futuro.

Evita falhas quando um módulo precisar de informação que não está
na RAM no momento — o Bridge guarda e devolve sob demanda.
"""

from __future__ import annotations

import json
import logging
import os
import threading
import time
from pathlib import Path
from typing import Any

from app.bridge.constants import DEFAULT_CONTINUITY_DIR, ContinuityNamespace

logger = logging.getLogger(__name__)


class ContinuityStore:
    """Cofre chave-valor com persistência em disco (JSON por namespace)."""

    def __init__(self, root: str | None = None) -> None:
        self._root = Path(root or os.getenv("YELENA_CONTINUITY_DIR", DEFAULT_CONTINUITY_DIR))
        self._root.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self._cache: dict[str, dict[str, Any]] = {}
        self._metrics = {"puts": 0, "gets": 0, "misses": 0, "deletes": 0}

    def _path(self, namespace: str) -> Path:
        safe = namespace.replace("/", "_").replace("..", "_")
        return self._root / f"{safe}.json"

    def _load_ns(self, namespace: str) -> dict[str, Any]:
        if namespace in self._cache:
            return self._cache[namespace]
        path = self._path(namespace)
        data: dict[str, Any] = {}
        if path.exists():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                logger.exception("continuity load failed", extra={"namespace": namespace})
                data = {}
        self._cache[namespace] = data
        return data

    def _save_ns(self, namespace: str) -> None:
        path = self._path(namespace)
        data = self._cache.get(namespace, {})
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(path)

    def put(
        self,
        namespace: str | ContinuityNamespace,
        key: str,
        value: Any,
        *,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        ns = namespace.value if isinstance(namespace, ContinuityNamespace) else namespace
        with self._lock:
            store = self._load_ns(ns)
            store[key] = {
                "value": value,
                "metadata": metadata or {},
                "updated_at": time.time(),
            }
            self._save_ns(ns)
            self._metrics["puts"] += 1

    def get(
        self,
        namespace: str | ContinuityNamespace,
        key: str,
        default: Any = None,
    ) -> Any:
        ns = namespace.value if isinstance(namespace, ContinuityNamespace) else namespace
        with self._lock:
            store = self._load_ns(ns)
            entry = store.get(key)
            if entry is None:
                self._metrics["misses"] += 1
                return default
            self._metrics["gets"] += 1
            return entry.get("value", default)

    def get_entry(
        self,
        namespace: str | ContinuityNamespace,
        key: str,
    ) -> dict[str, Any] | None:
        ns = namespace.value if isinstance(namespace, ContinuityNamespace) else namespace
        with self._lock:
            return self._load_ns(ns).get(key)

    def delete(self, namespace: str | ContinuityNamespace, key: str) -> bool:
        ns = namespace.value if isinstance(namespace, ContinuityNamespace) else namespace
        with self._lock:
            store = self._load_ns(ns)
            if key in store:
                del store[key]
                self._save_ns(ns)
                self._metrics["deletes"] += 1
                return True
            return False

    def list_keys(self, namespace: str | ContinuityNamespace) -> list[str]:
        ns = namespace.value if isinstance(namespace, ContinuityNamespace) else namespace
        with self._lock:
            return list(self._load_ns(ns).keys())

    def health(self) -> dict[str, Any]:
        return {
            "status": "healthy",
            "root": str(self._root),
            "metrics": dict(self._metrics),
        }
