"""Structured logging com redação básica."""

from __future__ import annotations

import re
from typing import Any

from app.observability.constants import LogLevel
from app.observability.models.log import LogRecord

SECRET_PATTERN = re.compile(
    r"(token|secret|password|api_key|apikey|authorization)",
    re.IGNORECASE,
)


def redact_fields(fields: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for k, v in fields.items():
        if SECRET_PATTERN.search(k):
            result[k] = "********"
        elif isinstance(v, dict):
            result[k] = redact_fields(v)
        else:
            result[k] = v
    return result


class StructuredLogger:
    def __init__(self, name: str = "yelena", max_records: int = 2000) -> None:
        self.name = name
        self._records: list[LogRecord] = []
        self._max = max_records

    def log(
        self,
        message: str,
        level: LogLevel = LogLevel.INFO,
        *,
        module: str | None = None,
        correlation_id: str | None = None,
        trace_id: str | None = None,
        **fields: Any,
    ) -> LogRecord:
        record = LogRecord(
            message=message,
            level=level,
            logger_name=self.name,
            module=module,
            correlation_id=correlation_id,
            trace_id=trace_id,
            fields=redact_fields(fields),
        )
        self._records.append(record)
        if len(self._records) > self._max:
            self._records = self._records[-self._max :]
        return record

    def info(self, message: str, **kwargs: Any) -> LogRecord:
        return self.log(message, LogLevel.INFO, **kwargs)

    def warning(self, message: str, **kwargs: Any) -> LogRecord:
        return self.log(message, LogLevel.WARNING, **kwargs)

    def error(self, message: str, **kwargs: Any) -> LogRecord:
        return self.log(message, LogLevel.ERROR, **kwargs)

    def recent(self, n: int = 50) -> list[LogRecord]:
        return self._records[-n:]
