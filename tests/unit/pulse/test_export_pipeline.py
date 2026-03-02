import time
from types import MappingProxyType

import pytest

from forge_base.pulse.basic_collector import ExecutionRecord
from forge_base.pulse.buffer import AsyncBuffer
from forge_base.pulse.context import ExecutionContext
from forge_base.pulse.export_pipeline import (
    ExportPipeline,
    _record_to_context,
    _record_to_dict,
)
from forge_base.pulse.exporters import InMemoryExporter
from forge_base.pulse.span import SpanRecord


def _make_record(**kwargs):
    defaults = {
        "correlation_id": "cid-1",
        "use_case_name": "TestUC",
        "value_track": "core",
        "subtrack": "",
        "feature": "",
        "duration_ms": 10.5,
        "success": True,
        "error_type": "",
        "timestamp": time.time(),
    }
    defaults.update(kwargs)
    return ExecutionRecord(**defaults)


def _make_span(**kwargs):
    defaults = {
        "span_id": "s1",
        "name": "db_query",
        "start_ns": 1000,
        "end_ns": 2000,
        "duration_ms": 0.001,
    }
    defaults.update(kwargs)
    return SpanRecord(**defaults)


@pytest.mark.pulse
class TestRecordToDict:
    def test_basic_fields(self):
        record = _make_record()
        d = _record_to_dict(record)
        assert d["correlation_id"] == "cid-1"
        assert d["use_case_name"] == "TestUC"
        assert d["value_track"] == "core"
        assert d["success"] is True
        assert "spans" not in d

    def test_with_spans(self):
        span = _make_span()
        record = _make_record(spans=[span])
        d = _record_to_dict(record)
        assert "spans" in d
        assert len(d["spans"]) == 1
        assert d["spans"][0]["name"] == "db_query"
        assert d["spans"][0]["span_id"] == "s1"

    def test_without_spans(self):
        record = _make_record(spans=[])
        d = _record_to_dict(record)
        assert "spans" not in d


@pytest.mark.pulse
class TestRecordToDictNewFields:
    def test_tags_included_when_present(self):
        record = _make_record(tags=MappingProxyType({"tier": "premium"}))
        d = _record_to_dict(record)
        assert d["tags"] == {"tier": "premium"}

    def test_tags_absent_when_empty(self):
        record = _make_record()
        d = _record_to_dict(record)
        assert "tags" not in d

    def test_extra_included_when_present(self):
        record = _make_record(extra=MappingProxyType({"debug": "1"}))
        d = _record_to_dict(record)
        assert d["extra"] == {"debug": "1"}

    def test_mapping_source_included_when_present(self):
        record = _make_record(mapping_source="spec")
        d = _record_to_dict(record)
        assert d["mapping_source"] == "spec"

    def test_mapping_source_absent_when_empty(self):
        record = _make_record()
        d = _record_to_dict(record)
        assert "mapping_source" not in d

    def test_dropped_spans_included_when_nonzero(self):
        record = _make_record(dropped_spans=5)
        d = _record_to_dict(record)
        assert d["dropped_spans"] == 5


@pytest.mark.pulse
class TestRecordToContext:
    def test_creates_context(self):
        record = _make_record(
            correlation_id="cid-42",
            use_case_name="MyUC",
            value_track="premium",
            subtrack="fast",
            feature="search",
        )
        ctx = _record_to_context(record)
        assert isinstance(ctx, ExecutionContext)
        assert ctx.correlation_id == "cid-42"
        assert ctx.use_case_name == "MyUC"
        assert ctx.value_track == "premium"
        assert ctx.subtrack == "fast"
        assert ctx.feature == "search"

    def test_context_propagates_tags(self):
        record = _make_record(tags=MappingProxyType({"tier": "premium"}))
        ctx = _record_to_context(record)
        assert ctx.tags["tier"] == "premium"

    def test_context_propagates_mapping_source(self):
        record = _make_record(mapping_source="spec")
        ctx = _record_to_context(record)
        assert ctx.mapping_source == "spec"


@pytest.mark.pulse
class TestExportPipeline:
    @pytest.mark.asyncio
    async def test_flush_calls_exporter(self):
        buf = AsyncBuffer(max_size=100)
        exporter = InMemoryExporter()
        pipeline = ExportPipeline(buf, exporter)

        record = _make_record()
        buf.push(record)

        count = await pipeline.flush()
        assert count == 1
        assert len(exporter.records) == 1
        ctx, data = exporter.records[0]
        assert data["correlation_id"] == "cid-1"

    @pytest.mark.asyncio
    async def test_empty_buffer(self):
        buf = AsyncBuffer(max_size=100)
        exporter = InMemoryExporter()
        pipeline = ExportPipeline(buf, exporter)

        count = await pipeline.flush()
        assert count == 0
        assert len(exporter.records) == 0

    @pytest.mark.asyncio
    async def test_multiple_records(self):
        buf = AsyncBuffer(max_size=100)
        exporter = InMemoryExporter()
        pipeline = ExportPipeline(buf, exporter)

        for i in range(3):
            buf.push(_make_record(correlation_id=f"cid-{i}"))

        count = await pipeline.flush()
        assert count == 3
        assert len(exporter.records) == 3

    @pytest.mark.asyncio
    async def test_flush_with_spans(self):
        buf = AsyncBuffer(max_size=100)
        exporter = InMemoryExporter()
        pipeline = ExportPipeline(buf, exporter)

        span = _make_span(name="cache_lookup")
        record = _make_record(spans=[span])
        buf.push(record)

        await pipeline.flush()
        _, data = exporter.records[0]
        assert "spans" in data
        assert data["spans"][0]["name"] == "cache_lookup"
