"""Carregamento controlado de módulos."""

from __future__ import annotations

import logging
from typing import Any

from app.core.constants import LifecycleState
from app.core.exceptions import LoaderError
from app.core.models.module import ModuleInfo
from app.core.registry import ModuleRegistry

logger = logging.getLogger(__name__)


class ModuleLoader:
    """Carrega e inicializa módulos de forma controlada e depurável."""

    def __init__(self, registry: ModuleRegistry) -> None:
        self._registry = registry

    async def load(self, module: ModuleInfo) -> None:
        """Carrega um módulo (initialize)."""
        if module.instance is None:
            raise LoaderError(
                f"Module has no instance: {module.id}",
                context={"module_id": module.id},
            )

        instance = module.instance
        if not hasattr(instance, "initialize"):
            raise LoaderError(
                f"Module instance missing initialize(): {module.id}",
                context={"module_id": module.id},
            )

        try:
            module.state = LifecycleState.STARTING
            await instance.initialize()
            logger.info("module loaded", extra={"module_id": module.id})
        except Exception as exc:
            module.state = LifecycleState.FAILED
            raise LoaderError(
                f"Failed to load module {module.id}: {exc}",
                context={"module_id": module.id, "error": str(exc)},
            ) from exc

    async def start(self, module: ModuleInfo) -> None:
        """Inicia um módulo já carregado."""
        if module.instance is None:
            raise LoaderError(
                f"Module has no instance: {module.id}",
                context={"module_id": module.id},
            )

        instance = module.instance
        if not hasattr(instance, "start"):
            # initialize-only modules are allowed
            module.state = LifecycleState.RUNNING
            return

        try:
            await instance.start()
            module.state = LifecycleState.RUNNING
            logger.info("module started", extra={"module_id": module.id})
        except Exception as exc:
            module.state = LifecycleState.FAILED
            raise LoaderError(
                f"Failed to start module {module.id}: {exc}",
                context={"module_id": module.id, "error": str(exc)},
            ) from exc

    async def load_many(self, modules: list[ModuleInfo]) -> list[str]:
        """Carrega vários módulos. Retorna IDs que falharam."""
        failed: list[str] = []
        for module in modules:
            try:
                await self.load(module)
            except LoaderError:
                failed.append(module.id)
                logger.exception("module load failed", extra={"module_id": module.id})
        return failed
