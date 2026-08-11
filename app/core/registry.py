"""Registro de módulos conhecidos pelo sistema."""

from __future__ import annotations

import logging
from typing import Iterator

from app.core.exceptions import RegistryError
from app.core.models.module import ModuleInfo
from app.core.types import ModuleId

logger = logging.getLogger(__name__)


class ModuleRegistry:
    """Registro central de módulos.

    Não controla lifecycle — apenas cataloga o que existe.
    """

    def __init__(self) -> None:
        self._modules: dict[ModuleId, ModuleInfo] = {}

    def register(self, module: ModuleInfo) -> None:
        if module.id in self._modules:
            raise RegistryError(
                f"Module already registered: {module.id}",
                context={"module_id": module.id},
            )
        self._modules[module.id] = module
        logger.info("module registered", extra={"module_id": module.id, "module_name": module.name})

    def unregister(self, module_id: ModuleId) -> ModuleInfo:
        if module_id not in self._modules:
            raise RegistryError(
                f"Module not found: {module_id}",
                context={"module_id": module_id},
            )
        module = self._modules.pop(module_id)
        logger.info("module unregistered", extra={"module_id": module_id})
        return module

    def get(self, module_id: ModuleId) -> ModuleInfo | None:
        return self._modules.get(module_id)

    def require(self, module_id: ModuleId) -> ModuleInfo:
        module = self.get(module_id)
        if module is None:
            raise RegistryError(
                f"Module not found: {module_id}",
                context={"module_id": module_id},
            )
        return module

    def has(self, module_id: ModuleId) -> bool:
        return module_id in self._modules

    def list_ids(self) -> list[ModuleId]:
        return list(self._modules.keys())

    def list_modules(self) -> list[ModuleInfo]:
        return list(self._modules.values())

    def __iter__(self) -> Iterator[ModuleInfo]:
        return iter(self._modules.values())

    def __len__(self) -> int:
        return len(self._modules)

    def __contains__(self, module_id: object) -> bool:
        return module_id in self._modules
