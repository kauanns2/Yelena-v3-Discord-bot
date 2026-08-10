"""Bootstrap do sistema — preparação inicial."""

from __future__ import annotations

import logging
from typing import Any

from app.core.constants import LifecycleState, ModulePriority
from app.core.dependency import DependencyResolver
from app.core.exceptions import BootstrapError
from app.core.health import HealthManager
from app.core.lifecycle import LifecycleManager
from app.core.loader import ModuleLoader
from app.core.metadata import ApplicationMetadata
from app.core.models.module import ModuleInfo
from app.core.registry import ModuleRegistry
from app.core.shutdown import ShutdownManager
from app.core.state import StateManager
from app.core.version import CORE_MODULE_ID, CORE_MODULE_NAME, CORE_VERSION

logger = logging.getLogger(__name__)


class Bootstrap:
    """Prepara o ambiente e cria os serviços centrais do Core.

    Não contém lógica de Discord, IA, memória ou personalidade.
    """

    def __init__(self, environment: str = "development") -> None:
        self.environment = environment
        self.metadata = ApplicationMetadata(environment=environment)
        self.lifecycle = LifecycleManager(source="core")
        self.registry = ModuleRegistry()
        self.state = StateManager()
        self.health = HealthManager()
        self.resolver = DependencyResolver(self.registry)
        self.loader = ModuleLoader(self.registry)
        self.shutdown = ShutdownManager(self.registry, self.resolver)

    def prepare(self) -> None:
        """Valida pré-condições e registra o próprio Core."""
        try:
            self.lifecycle.transition(LifecycleState.BOOTSTRAPPING, reason="bootstrap.prepare")
            self.state.set_lifecycle(LifecycleState.BOOTSTRAPPING)
            self.state.set_environment(self.environment)

            # Registrar o Core como módulo
            core_module = ModuleInfo(
                id=CORE_MODULE_ID,
                name=CORE_MODULE_NAME,
                version=CORE_VERSION,
                description="Fundação operacional da Yelena V3",
                priority=ModulePriority.CRITICAL,
                metadata={"is_core": True},
            )
            if not self.registry.has(CORE_MODULE_ID):
                self.registry.register(core_module)

            logger.info(
                "bootstrap prepared",
                extra={
                    "version": self.metadata.version,
                    "environment": self.environment,
                },
            )
        except Exception as exc:
            self.lifecycle.transition(LifecycleState.FAILED, reason=str(exc))
            self.state.set_lifecycle(LifecycleState.FAILED)
            self.state.add_error(str(exc))
            raise BootstrapError(
                f"Bootstrap failed: {exc}",
                context={"environment": self.environment},
            ) from exc

    def create_kernel(self) -> "Kernel":
        from app.core.kernel import Kernel

        return Kernel(bootstrap=self)
