"""Tool Registry."""

from __future__ import annotations

import logging

from app.actions.errors import ToolNotFoundError
from app.actions.models.tool import Tool
from app.actions.types import ToolId

logger = logging.getLogger(__name__)


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[ToolId, Tool] = {}

    def register(self, tool: Tool) -> None:
        self._tools[tool.id] = tool
        logger.info("tool registered", extra={"tool_id": tool.id, "risk": tool.risk.value})

    def unregister(self, tool_id: ToolId) -> None:
        self._tools.pop(tool_id, None)

    def get(self, tool_id: ToolId) -> Tool | None:
        return self._tools.get(tool_id)

    def require(self, tool_id: ToolId) -> Tool:
        tool = self.get(tool_id)
        if tool is None:
            raise ToolNotFoundError(f"Tool not found: {tool_id}", context={"tool_id": tool_id})
        if not tool.enabled:
            raise ToolNotFoundError(f"Tool disabled: {tool_id}", context={"tool_id": tool_id})
        return tool

    def list_tools(self) -> list[Tool]:
        return list(self._tools.values())

    def list_ids(self) -> list[str]:
        return list(self._tools.keys())
