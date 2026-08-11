"""Metric sample."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
import time


@dataclass(slots=True)
class MetricSample:
    name: str
    value: float
    metric_type: str = "gauge"  # counter | gauge | histogram
    labels: dict[str, str] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "value": self.value,
            "metric_type": self.metric_type,
            "labels": self.labels,
            "timestamp": self.timestamp,
        }
