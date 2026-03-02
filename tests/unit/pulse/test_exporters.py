import io
import json

import pytest

from forge_base.pulse.context import ExecutionContext
from forge_base.pulse.exporters import InMemoryExporter, JsonLinesExporter
from forge_base.pulse.protocols import PulseExporterProtocol


def _make_ctx(**kwargs):
    return ExecutionContext.build(
        use_case_name=kwargs.get("use_case_name", "TestUC"),
        value_track=kwargs.get("value_track", "core"),
    )


@pytest.mark.pulse
class TestJsonLinesExporter:
    def test_writes_json_line(self):
        stream = io.StringIO()
        exporter = JsonLinesExporter(stream)
        ctx = _make_ctx()
        exporter.export(ctx, {"key": "value"})
        line = stream.getvalue()
        assert line.endswith("\n")
        parsed = json.loads(line.strip())
        assert parsed == {"key": "value"}

    def test_multiple_records(self):
        stream = io.StringIO()
        exporter = JsonLinesExporter(stream)
        ctx = _make_ctx()
        exporter.export(ctx, {"a": 1})
        exporter.export(ctx, {"b": 2})
        lines = stream.getvalue().strip().split("\n")
        assert len(lines) == 2
        assert json.loads(lines[0]) == {"a": 1}
        assert json.loads(lines[1]) == {"b": 2}

    def test_default_str_for_timestamps(self):
        stream = io.StringIO()
        exporter = JsonLinesExporter(stream)
        ctx = _make_ctx()
        from datetime import datetime

        dt = datetime(2024, 1, 15, 12, 0, 0)
        exporter.export(ctx, {"ts": dt})
        parsed = json.loads(stream.getvalue().strip())
        assert parsed["ts"] == str(dt)

    def test_compact_separators(self):
        stream = io.StringIO()
        exporter = JsonLinesExporter(stream)
        ctx = _make_ctx()
        exporter.export(ctx, {"key": "value", "num": 42})
        line = stream.getvalue().strip()
        # compact separators: no spaces after , and :
        assert " " not in line

    def test_spans_included(self):
        stream = io.StringIO()
        exporter = JsonLinesExporter(stream)
        ctx = _make_ctx()
        data = {
            "correlation_id": "abc",
            "spans": [
                {"span_id": "s1", "name": "db_query", "duration_ms": 1.5},
            ],
        }
        exporter.export(ctx, data)
        parsed = json.loads(stream.getvalue().strip())
        assert len(parsed["spans"]) == 1
        assert parsed["spans"][0]["name"] == "db_query"


@pytest.mark.pulse
class TestInMemoryExporter:
    def test_stores_records(self):
        exporter = InMemoryExporter()
        ctx = _make_ctx()
        exporter.export(ctx, {"a": 1})
        assert len(exporter.records) == 1
        assert exporter.records[0] == (ctx, {"a": 1})

    def test_records_returns_copy(self):
        exporter = InMemoryExporter()
        ctx = _make_ctx()
        exporter.export(ctx, {"a": 1})
        r1 = exporter.records
        r2 = exporter.records
        assert r1 == r2
        assert r1 is not r2

    def test_empty_initially(self):
        exporter = InMemoryExporter()
        assert exporter.records == []

    def test_multiple_exports(self):
        exporter = InMemoryExporter()
        ctx1 = _make_ctx(use_case_name="UC1")
        ctx2 = _make_ctx(use_case_name="UC2")
        exporter.export(ctx1, {"x": 1})
        exporter.export(ctx2, {"x": 2})
        assert len(exporter.records) == 2


@pytest.mark.pulse
class TestProtocolConformance:
    def test_jsonlines_satisfies_protocol(self):
        stream = io.StringIO()
        exporter = JsonLinesExporter(stream)
        assert isinstance(exporter, PulseExporterProtocol)

    def test_inmemory_satisfies_protocol(self):
        exporter = InMemoryExporter()
        assert isinstance(exporter, PulseExporterProtocol)
