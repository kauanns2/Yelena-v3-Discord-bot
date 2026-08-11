"""Log record estruturado."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
import time
import uuid

from app.observability.constants import LogLevel


@dataclass(slots=True)
class LogRecord:
    message: str
    level: LogLevel = LogLevel.INFO
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    logger_name: str = "yelena"
    correlation_id: str | None = None
    trace_id: str | None = None
    module: str | None = None
    timestamp: float = field(default_factory=time.time)
    fields: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "level": self.level.value,
            "message": self.message,
            "logger_name": self.logger_name,
            "correlation_id": self.correlation_id,
            "trace_id": self.trace_id,
            "module": self.module,
            "timestamp": self.timestamp,
            "fields": self.fields,
        }
