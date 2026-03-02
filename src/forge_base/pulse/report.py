from __future__ import annotations

from dataclasses import dataclass, field
import time
from typing import TYPE_CHECKING, Any, Protocol

from forge_base.pulse.level import MonitoringLevel

if TYPE_CHECKING:
    from forge_base.pulse.basic_collector import ExecutionRecord


class _MetricsReporter(Protocol):
    def report(self) -> dict[str, Any]: ...


@dataclass
class HistogramStats:
    count: int
    sum: float
    mean: float
    min: float
    max: float
    p50: float
    p95: float
    p99: float


@dataclass
class PulseSnapshot:
    timestamp: float
    schema_version: str
    level: MonitoringLevel
    executions: list[dict[str, Any]] = field(default_factory=list)
    counters: dict[str, Any] = field(default_factory=dict)
    histograms: dict[str, HistogramStats] = field(default_factory=dict)

    @classmethod
    def from_records(
        cls,
        records: list[ExecutionRecord],
        metrics: _MetricsReporter,
        level: MonitoringLevel,
        schema_version: str,
    ) -> PulseSnapshot:
        report = metrics.report()

        executions = [
            {
                "correlation_id": r.correlation_id,
                "use_case_name": r.use_case_name,
                "value_track": r.value_track,
                "subtrack": r.subtrack,
                "feature": r.feature,
                "duration_ms": r.duration_ms,
                "success": r.success,
                "error_type": r.error_type,
                "timestamp": r.timestamp,
            }
            for r in records
        ]

        histograms: dict[str, HistogramStats] = {}
        for key, hist_data in report.get("histograms", {}).items():
            if isinstance(hist_data, dict):
                histograms[key] = HistogramStats(
                    count=hist_data.get("count", 0),
                    sum=hist_data.get("sum", 0.0),
                    mean=hist_data.get("mean", 0.0),
                    min=hist_data.get("min", 0.0),
                    max=hist_data.get("max", 0.0),
                    p50=hist_data.get("p50", hist_data.get("median", 0.0)),
                    p95=hist_data.get("p95", 0.0),
                    p99=hist_data.get("p99", 0.0),
                )

        return cls(
            timestamp=time.time(),
            schema_version=schema_version,
            level=level,
            executions=executions,
            counters=report.get("counters", {}),
            histograms=histograms,
        )
