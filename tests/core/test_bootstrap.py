"""Testes de bootstrap e kernel."""

import pytest

from app.core.bootstrap import Bootstrap
from app.core.constants import LifecycleState


def test_bootstrap_prepare():
    bootstrap = Bootstrap(environment="testing")
    bootstrap.prepare()
    assert bootstrap.lifecycle.state == LifecycleState.BOOTSTRAPPING
    assert bootstrap.registry.has("core")
    assert bootstrap.state.state.environment == "testing"


@pytest.mark.asyncio
async def test_kernel_start_stop():
    bootstrap = Bootstrap(environment="testing")
    bootstrap.prepare()
    kernel = bootstrap.create_kernel()

    await kernel.start()
    assert kernel.is_running
    assert kernel.lifecycle.state in {LifecycleState.RUNNING, LifecycleState.DEGRADED}

    result = await kernel.stop()
    assert kernel.lifecycle.state == LifecycleState.STOPPED
    assert "results" in result


@pytest.mark.asyncio
async def test_kernel_status():
    bootstrap = Bootstrap(environment="testing")
    bootstrap.prepare()
    kernel = bootstrap.create_kernel()
    await kernel.start()

    status = kernel.status()
    assert status["version"]
    assert status["lifecycle"]
    assert "modules" in status

    await kernel.stop()
