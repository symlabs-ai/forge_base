from __future__ import annotations

from typing import TYPE_CHECKING, Any

from forge_base.pulse.context import ExecutionContext

if TYPE_CHECKING:
    from forge_base.pulse.basic_collector import ExecutionRecord
    from forge_base.pulse.buffer import AsyncBuffer
    from forge_base.pulse.protocols import PulseExporterProtocol
    from forge_base.pulse.span import SpanRecord


def _span_to_dict(span: SpanRecord) -> dict[str, Any]:
    d: dict[str, Any] = {
        "span_id": span.span_id,
        "name": span.name,
        "start_ns": span.start_ns,
        "end_ns": span.end_ns,
        "duration_ms": span.duration_ms,
    }
    if span.parent_span_id:
        d["parent_span_id"] = span.parent_span_id
    if span.attributes:
        d["attributes"] = dict(span.attributes)
    return d


def _record_to_dict(record: ExecutionRecord) -> dict[str, Any]:
    d: dict[str, Any] = {
        "correlation_id": record.correlation_id,
        "use_case_name": record.use_case_name,
        "value_track": record.value_track,
        "subtrack": record.subtrack,
        "feature": record.feature,
        "duration_ms": record.duration_ms,
        "success": record.success,
        "error_type": record.error_type,
        "timestamp": record.timestamp,
        "track_type": record.track_type,
    }
    if record.supports:
        d["supports"] = list(record.supports)
    if record.mapping_source:
        d["mapping_source"] = record.mapping_source
    if record.tags:
        d["tags"] = dict(record.tags)
    if record.extra:
        d["extra"] = dict(record.extra)
    if record.dropped_spans:
        d["dropped_spans"] = record.dropped_spans
    if record.spans:
        d["spans"] = [_span_to_dict(s) for s in record.spans]
    return d


def _record_to_context(record: ExecutionRecord) -> ExecutionContext:
    return ExecutionContext.build(
        correlation_id=record.correlation_id,
        use_case_name=record.use_case_name,
        value_track=record.value_track,
        subtrack=record.subtrack,
        feature=record.feature,
        tags=dict(record.tags) if record.tags else None,
        mapping_source=record.mapping_source,
        track_type=record.track_type,
        supports=record.supports,
    )


class ExportPipeline:
    __slots__ = ("_buffer", "_exporter")

    def __init__(self, buffer: AsyncBuffer, exporter: PulseExporterProtocol) -> None:
        self._buffer = buffer
        self._exporter = exporter

    async def flush(self) -> int:
        def _handler(record: ExecutionRecord) -> None:
            ctx = _record_to_context(record)
            data = _record_to_dict(record)
            self._exporter.export(ctx, data)

        return await self._buffer.flush(_handler)
