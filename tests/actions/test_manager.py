"""Testes do Action Manager."""

from app.actions import ActionManager
from app.actions.models.request import ActionRequest
from app.actions.constants import ActionStatus, RiskLevel
from app.actions.models.tool import Tool, ToolCapabilities
from app.actions.constants import ToolCategory


def test_echo_tool():
    am = ActionManager()
    am.start()
    result = am.execute(ActionRequest(tool_id="echo", arguments={"message": "oi"}))
    assert result.success
    assert result.output["echo"] == "oi"


def test_missing_tool():
    am = ActionManager()
    am.start()
    result = am.execute(ActionRequest(tool_id="nonexistent", arguments={}))
    assert not result.success
    assert result.status == ActionStatus.FAILED or result.status == ActionStatus.DENIED


def test_high_risk_requires_confirmation():
    am = ActionManager()
    am.start()

    def dangerous(**kwargs):
        return {"done": True}

    am.register_tool(
        Tool(
            id="dangerous",
            name="Dangerous",
            risk=RiskLevel.HIGH,
            capabilities=ToolCapabilities(requires_confirmation=True),
            handler=dangerous,
        )
    )
    result = am.execute(ActionRequest(tool_id="dangerous", arguments={}))
    assert result.status == ActionStatus.AWAITING_CONFIRMATION

    result2 = am.execute(
        ActionRequest(tool_id="dangerous", arguments={}, confirmed=True)
    )
    assert result2.success


def test_dry_run():
    am = ActionManager()
    am.start()
    result = am.execute(
        ActionRequest(tool_id="echo", arguments={"message": "x"}, dry_run=True)
    )
    assert result.success
    assert result.dry_run
