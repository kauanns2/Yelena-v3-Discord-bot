"""Kernel — núcleo coordenador da aplicação.

Coordena serviços. Não é um God Object.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from app.core.constants import LifecycleState, HealthStatus
from app.core.exceptions import CoreError, LifecycleError
from app.core.models.module import ModuleInfo
from app.core.protocols import HealthCheckResult
from app.core.version import YELENA_VERSION, CORE_VERSION

if TYPE_CHECKING:
    from app.core.bootstrap import Bootstrap

logger = logging.getLogger(__name__)


class Kernel:
    """Núcleo central da Yelena V3.

    Responsabilidades:
    - coordenar lifecycle
    - expor registry / dependency / health / state
    - iniciar e parar o sistema
    - não conter lógica de domínio (memória, emoção, Discord, etc.)
    """

    def __init__(self, bootstrap: Bootstrap) -> None:
        self._bootstrap = bootstrap
        self.lifecycle = bootstrap.lifecycle
        self.registry = bootstrap.registry
        self.state = bootstrap.state
        self.health = bootstrap.health
        self.resolver = bootstrap.resolver
        self.loader = bootstrap.loader
        self.shutdown_manager = bootstrap.shutdown
        self.metadata = bootstrap.metadata

    @property
    def version(self) -> str:
        return YELENA_VERSION

    @property
    def core_version(self) -> str:
        return CORE_VERSION

    @property
    def is_running(self) -> bool:
        return self.lifecycle.state in {LifecycleState.RUNNING, LifecycleState.DEGRADED}

    def register_module(self, module: ModuleInfo) -> None:
        self.registry.register(module)

    async def start(self) -> None:
        """Inicia o sistema: valida deps, carrega e sobe módulos."""
        if self.lifecycle.state not in {LifecycleState.BOOTSTRAPPING, LifecycleState.CREATED}:
            if self.lifecycle.state == LifecycleState.CREATED:
                self._bootstrap.prepare()
            else:
                raise LifecycleError(
                    f"Cannot start from state: {self.lifecycle.state.value}",
                )

        try:
            self.lifecycle.transition(LifecycleState.STARTING, reason="kernel.start")
            self.state.set_lifecycle(LifecycleState.STARTING)

            # Validar dependências
            self.resolver.validate()
            order = self.resolver.resolve_order()
            logger.info("startup order resolved", extra={"order": order})

            # Carregar e iniciar módulos (exceto core já registrado)
            failed: list[str] = []
            for module_id in order:
                if module_id == "core":
                    continue
                module = self.registry.require(module_id)
                try:
                    await self.loader.load(module)
                    await self.loader.start(module)
                except Exception:
                    failed.append(module_id)
                    logger.exception("module failed during start", extra={"module_id": module_id})

            if failed:
                self.lifecycle.transition(
                    LifecycleState.DEGRADED,
                    reason=f"modules failed: {failed}",
                )
                self.state.set_lifecycle(LifecycleState.DEGRADED)
                self.state.set_health(HealthStatus.DEGRADED)
                for f in failed:
                    self.state.add_error(f"module failed: {f}")
            else:
                self.lifecycle.transition(LifecycleState.RUNNING, reason="all modules started")
                self.state.set_lifecycle(LifecycleState.RUNNING)
                self.state.set_health(HealthStatus.HEALTHY)

            # Registrar health do core
            self.health.register("core", self._core_health_check)

            logger.info(
                "kernel started",
                extra={
                    "state": self.lifecycle.state.value,
                    "modules": len(self.registry),
                    "failed": failed,
                },
            )
        except Exception as exc:
            try:
                self.lifecycle.transition(LifecycleState.FAILED, reason=str(exc))
            except LifecycleError:
                pass
            self.state.set_lifecycle(LifecycleState.FAILED)
            self.state.set_health(HealthStatus.UNHEALTHY)
            self.state.add_error(str(exc))
            raise CoreError(f"Kernel start failed: {exc}") from exc

    async def stop(self) -> dict[str, Any]:
        """Encerra o sistema de forma segura."""
        if self.lifecycle.state in {LifecycleState.STOPPED, LifecycleState.STOPPING}:
            return {"status": "already_stopped"}

        try:
            if self.lifecycle.can_transition(LifecycleState.STOPPING):
                self.lifecycle.transition(LifecycleState.STOPPING, reason="kernel.stop")
            self.state.set_lifecycle(LifecycleState.STOPPING)

            result = await self.shutdown_manager.shutdown_all()

            if self.lifecycle.can_transition(LifecycleState.STOPPED):
                self.lifecycle.transition(LifecycleState.STOPPED, reason="shutdown complete")
            self.state.set_lifecycle(LifecycleState.STOPPED)

            logger.info("kernel stopped", extra=result)
            return result
        except Exception as exc:
            self.state.add_error(str(exc))
            raise CoreError(f"Kernel stop failed: {exc}") from exc

    async def health_check(self) -> HealthCheckResult:
        return await self.health.aggregate()

    async def _core_health_check(self) -> HealthCheckResult:
        status = HealthStatus.HEALTHY
        if self.lifecycle.state == LifecycleState.DEGRADED:
            status = HealthStatus.DEGRADED
        elif self.lifecycle.state in {LifecycleState.FAILED, LifecycleState.STOPPED}:
            status = HealthStatus.UNHEALTHY
        elif self.lifecycle.state != LifecycleState.RUNNING:
            status = HealthStatus.UNKNOWN

        return HealthCheckResult(
            status=status,
            message=f"Core state: {self.lifecycle.state.value}",
            details=self.state.snapshot(),
        )

    def status(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "core_version": self.core_version,
            "lifecycle": self.lifecycle.state.value,
            "health": self.state.state.health.value,
            "modules": [m.to_dict() for m in self.registry.list_modules()],
            "state": self.state.snapshot(),
            "metadata": self.metadata.to_dict(),
        }
