from __future__ import annotations

from dataclasses import dataclass, field
import threading
import time
from types import MappingProxyType
from typing import TYPE_CHECKING, Any

from forge_base.pulse.context import _EMPTY_TAGS, ExecutionContext
from forge_base.pulse.field_names import PulseFieldNames
from forge_base.pulse.level import MonitoringLevel
from forge_base.pulse.protocols import PulseMetricsProtocol
from forge_base.pulse.span import SpanRecord, _span_accumulator

if TYPE_CHECKING:
    from forge_base.pulse.report import PulseSnapshot


_EMPTY_EXTRA: MappingProxyType[str, Any] = MappingProxyType({})


@dataclass
class ExecutionRecord:
    correlation_id: str
    use_case_name: str
    value_track: str
    subtrack: str
    feature: str
    duration_ms: float
    success: bool
    error_type: str
    timestamp: float = field(default_factory=time.time)
    spans: list[SpanRecord] = field(default_factory=list)
    tags: MappingProxyType[str, str] = field(default_factory=lambda: _EMPTY_TAGS)
    extra: MappingProxyType[str, Any] = field(default_factory=lambda: _EMPTY_EXTRA)
    mapping_source: str = ""
    dropped_spans: int = 0


class BasicCollector:
    __slots__ = ("_metrics", "_level", "_lock", "_starts", "_outcomes", "_records")

    def __init__(
        self,
        metrics: PulseMetricsProtocol,
        level: MonitoringLevel = MonitoringLevel.BASIC,
    ) -> None:
        self._metrics = metrics
        self._level = level
        self._lock = threading.Lock()
        self._starts: dict[str, int] = {}
        self._outcomes: dict[str, str] = {}
        self._records: list[ExecutionRecord] = []

    def _basic_labels(self, ctx: ExecutionContext) -> dict[str, str]:
        return {
            "use_case": ctx.use_case_name,
            "value_track": ctx.value_track,
        }

    def _standard_labels(self, ctx: ExecutionContext) -> dict[str, str]:
        return {
            "use_case": ctx.use_case_name,
            "value_track": ctx.value_track,
            "subtrack": ctx.subtrack,
        }

    def _detailed_labels(self, ctx: ExecutionContext) -> dict[str, str]:
        return {
            "use_case": ctx.use_case_name,
            "value_track": ctx.value_track,
            "subtrack": ctx.subtrack,
            "feature": ctx.feature,
        }

    def on_start(self, context: ExecutionContext) -> None:
        cid = context.correlation_id
        start_ns = time.perf_counter_ns()
        with self._lock:
            self._starts[cid] = start_ns
            self._outcomes[cid] = ""
        labels = self._basic_labels(context)
        self._metrics.increment(PulseFieldNames.PULSE_EXEC_COUNT, 1, **labels)
        if self._level >= MonitoringLevel.STANDARD:
            self._metrics.increment(
                PulseFieldNames.PULSE_EXEC_COUNT, 1, **self._standard_labels(context)
            )
        if self._level >= MonitoringLevel.DETAILED:
            self._metrics.increment(
                PulseFieldNames.PULSE_EXEC_COUNT, 1, **self._detailed_labels(context)
            )

    def on_success(self, context: ExecutionContext, result: Any) -> None:
        labels = self._basic_labels(context)
        self._metrics.increment(PulseFieldNames.PULSE_EXEC_SUCCESS, 1, **labels)
        if self._level >= MonitoringLevel.STANDARD:
            self._metrics.increment(
                PulseFieldNames.PULSE_EXEC_SUCCESS, 1, **self._standard_labels(context)
            )
        if self._level >= MonitoringLevel.DETAILED:
            self._metrics.increment(
                PulseFieldNames.PULSE_EXEC_SUCCESS, 1, **self._detailed_labels(context)
            )

    def on_error(self, context: ExecutionContext, error: Exception) -> None:
        cid = context.correlation_id
        error_type = type(error).__name__
        with self._lock:
            self._outcomes[cid] = error_type
        labels = self._basic_labels(context)
        self._metrics.increment(PulseFieldNames.PULSE_EXEC_ERRORS, 1, **labels)
        if self._level >= MonitoringLevel.STANDARD:
            self._metrics.increment(
                PulseFieldNames.PULSE_EXEC_ERRORS, 1, **self._standard_labels(context)
            )
        if self._level >= MonitoringLevel.DETAILED:
            self._metrics.increment(
                PulseFieldNames.PULSE_EXEC_ERRORS, 1, **self._detailed_labels(context)
            )

    def on_finish(self, context: ExecutionContext) -> None:
        cid = context.correlation_id
        end_ns = time.perf_counter_ns()
        with self._lock:
            start_ns = self._starts.pop(cid, end_ns)
            error_type = self._outcomes.pop(cid, "")

        duration_ms = (end_ns - start_ns) / 1_000_000

        labels = self._basic_labels(context)
        self._metrics.histogram(PulseFieldNames.PULSE_EXEC_DURATION_MS, duration_ms, **labels)
        if self._level >= MonitoringLevel.STANDARD:
            self._metrics.histogram(
                PulseFieldNames.PULSE_EXEC_DURATION_MS,
                duration_ms,
                **self._standard_labels(context),
            )
        if self._level >= MonitoringLevel.DETAILED:
            self._metrics.histogram(
                PulseFieldNames.PULSE_EXEC_DURATION_MS,
                duration_ms,
                **self._detailed_labels(context),
            )

        acc = _span_accumulator.get()
        spans = acc.harvest() if acc is not None else []
        dropped = acc.dropped_count if acc is not None else 0

        record = ExecutionRecord(
            correlation_id=cid,
            use_case_name=context.use_case_name,
            value_track=context.value_track,
            subtrack=context.subtrack,
            feature=context.feature,
            duration_ms=duration_ms,
            success=(error_type == ""),
            error_type=error_type,
            spans=spans,
            tags=context.tags if self._level >= MonitoringLevel.DETAILED else _EMPTY_TAGS,
            extra=context.extra if self._level >= MonitoringLevel.DIAGNOSTIC else _EMPTY_EXTRA,
            mapping_source=context.mapping_source if self._level >= MonitoringLevel.DIAGNOSTIC else "",
            dropped_spans=dropped if self._level >= MonitoringLevel.DIAGNOSTIC else 0,
        )
        with self._lock:
            self._records.append(record)

    def snapshot(self) -> PulseSnapshot:
        from forge_base.pulse.report import PulseSnapshot

        with self._lock:
            records = list(self._records)
        return PulseSnapshot.from_records(
            records=records,
            metrics=self._metrics,
            level=self._level,
            schema_version=_get_schema_version(),
        )

    def clear_records(self) -> None:
        with self._lock:
            self._records.clear()


def _get_schema_version() -> str:
    from forge_base.pulse._version import PULSE_SCHEMA_VERSION

    return PULSE_SCHEMA_VERSION
