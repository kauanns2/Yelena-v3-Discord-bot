"""Metrics registry."""

from __future__ import annotations

from app.observability.models.metric import MetricSample


class MetricsRegistry:
    def __init__(self) -> None:
        self._counters: dict[str, float] = {}
        self._gauges: dict[str, float] = {}
        self._samples: list[MetricSample] = []
        self._max_samples = 5000

    def incr(self, name: str, value: float = 1.0, **labels: str) -> None:
        key = self._key(name, labels)
        self._counters[key] = self._counters.get(key, 0.0) + value
        self._add_sample(name, self._counters[key], "counter", labels)

    def set_gauge(self, name: str, value: float, **labels: str) -> None:
        key = self._key(name, labels)
        self._gauges[key] = value
        self._add_sample(name, value, "gauge", labels)

    def get_counter(self, name: str, **labels: str) -> float:
        return self._counters.get(self._key(name, labels), 0.0)

    def get_gauge(self, name: str, **labels: str) -> float:
        return self._gauges.get(self._key(name, labels), 0.0)

    def snapshot(self) -> dict[str, float]:
        data = {**self._counters, **self._gauges}
        return data

    def _key(self, name: str, labels: dict[str, str]) -> str:
        if not labels:
            return name
        label_str = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
        return f"{name}{{{label_str}}}"

    def _add_sample(self, name: str, value: float, metric_type: str, labels: dict[str, str]) -> None:
        self._samples.append(
            MetricSample(name=name, value=value, metric_type=metric_type, labels=dict(labels))
        )
        if len(self._samples) > self._max_samples:
            self._samples = self._samples[-self._max_samples :]
