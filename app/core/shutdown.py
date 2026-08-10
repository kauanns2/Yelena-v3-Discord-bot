"""Encerramento seguro respeitando dependências."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from app.core.constants import LifecycleState, DEFAULT_SHUTDOWN_TIMEOUT
from app.core.dependency import DependencyResolver
from app.core.exceptions import ShutdownError
from app.core.registry import ModuleRegistry

logger = logging.getLogger(__name__)


class ShutdownManager:
    """Controla shutdown ordenado dos módulos."""

    def __init__(
        self,
        registry: ModuleRegistry,
        resolver: DependencyResolver,
        timeout: float = DEFAULT_SHUTDOWN_TIMEOUT,
    ) -> None:
        self._registry = registry
        self._resolver = resolver
        self._timeout = timeout

    async def shutdown_all(self) -> dict[str, Any]:
        """Desliga todos os módulos na ordem correta.

        Se A depende de B, A encerra antes de B.
        Falhas em um módulo não impedem o restante.
        """
        results: dict[str, str] = {}
        try:
            order = self._resolver.shutdown_order()
        except Exception:
            # fallback: ordem de registro invertida
            order = list(reversed(self._registry.list_ids()))
            logger.warning("using fallback shutdown order")

        for module_id in order:
            module = self._registry.get(module_id)
            if module is None:
                continue
            if module.state in {LifecycleState.STOPPED, LifecycleState.CREATED}:
                results[module_id] = "already_stopped"
                continue

            try:
                await asyncio.wait_for(
                    self._stop_module(module),
                    timeout=self._timeout,
                )
                module.state = LifecycleState.STOPPED
                results[module_id] = "stopped"
                logger.info("module stopped", extra={"module_id": module_id})
            except asyncio.TimeoutError:
                module.state = LifecycleState.FAILED
                results[module_id] = "timeout"
                logger.error("module shutdown timeout", extra={"module_id": module_id})
            except Exception as exc:
                module.state = LifecycleState.FAILED
                results[module_id] = f"error: {exc}"
                logger.exception("module shutdown failed", extra={"module_id": module_id})

        return {"order": order, "results": results}

    async def _stop_module(self, module: Any) -> None:
        module.state = LifecycleState.STOPPING
        instance = module.instance
        if instance is not None and hasattr(instance, "stop"):
            await instance.stop()
