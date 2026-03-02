from types import MappingProxyType

import pytest

from forge_base.pulse.basic_collector import ExecutionRecord
from forge_base.pulse.level import MonitoringLevel
from forge_base.pulse.report import HistogramStats, PulseSnapshot
from forge_base.pulse.span import SpanRecord
from forge_base.testing.fakes.fake_metrics_collector import FakeMetricsCollector


def _make_records(n: int = 3) -> list[ExecutionRecord]:
    records = []
    for i in range(n):
        records.append(
            ExecutionRecord(
                correlation_id=f"cid-{i}",
                use_case_name="TestUseCase",
                value_track="legacy",
                subtrack="billing",
                feature="create",
                duration_ms=float(i + 1),
                success=(i != 1),
                error_type="" if i != 1 else "ValueError",
            )
        )
    return records


@pytest.mark.pulse
class TestPulseSnapshot:
    def test_from_records_creates_snapshot(self):
        metrics = FakeMetricsCollector()
        metrics.increment("pulse.execution.count", use_case="TestUseCase", value_track="legacy")
        metrics.histogram(
            "pulse.execution.duration_ms", 5.0, use_case="TestUseCase", value_track="legacy"
        )
        records = _make_records()

        snap = PulseSnapshot.from_records(
            records=records,
            metrics=metrics,
            level=MonitoringLevel.BASIC,
            schema_version="0.2",
        )

        assert snap.schema_version == "0.2"
        assert snap.level == MonitoringLevel.BASIC
        assert len(snap.executions) == 3
        assert snap.timestamp > 0

    def test_executions_contain_correct_fields(self):
        metrics = FakeMetricsCollector()
        records = _make_records(1)

        snap = PulseSnapshot.from_records(
            records=records,
            metrics=metrics,
            level=MonitoringLevel.BASIC,
            schema_version="0.2",
        )

        exec_data = snap.executions[0]
        assert exec_data["correlation_id"] == "cid-0"
        assert exec_data["use_case_name"] == "TestUseCase"
        assert exec_data["value_track"] == "legacy"
        assert exec_data["subtrack"] == "billing"
        assert exec_data["feature"] == "create"
        assert exec_data["duration_ms"] == 1.0
        assert exec_data["success"] is True
        assert exec_data["error_type"] == ""

    def test_counters_populated_from_metrics(self):
        metrics = FakeMetricsCollector()
        metrics.increment("pulse.execution.count", use_case="Test", value_track="legacy")
        metrics.increment("pulse.execution.count", use_case="Test", value_track="legacy")

        snap = PulseSnapshot.from_records(
            records=[],
            metrics=metrics,
            level=MonitoringLevel.BASIC,
            schema_version="0.2",
        )

        key = "pulse.execution.count{use_case=Test,value_track=legacy}"
        assert snap.counters[key] == 2

    def test_histograms_populated_from_metrics(self):
        metrics = FakeMetricsCollector()
        metrics.histogram("pulse.execution.duration_ms", 5.0)
        metrics.histogram("pulse.execution.duration_ms", 15.0)

        snap = PulseSnapshot.from_records(
            records=[],
            metrics=metrics,
            level=MonitoringLevel.BASIC,
            schema_version="0.2",
        )

        assert "pulse.execution.duration_ms" in snap.histograms
        hist = snap.histograms["pulse.execution.duration_ms"]
        assert isinstance(hist, HistogramStats)
        assert hist.count == 2
        assert hist.sum == 20.0
        assert hist.min == 5.0
        assert hist.max == 15.0

    def test_empty_snapshot(self):
        metrics = FakeMetricsCollector()
        snap = PulseSnapshot.from_records(
            records=[],
            metrics=metrics,
            level=MonitoringLevel.BASIC,
            schema_version="0.2",
        )
        assert snap.executions == []
        assert snap.counters == {}
        assert snap.histograms == {}


def _make_span(**kwargs):
    defaults = {
        "span_id": "s1",
        "name": "db_query",
        "start_ns": 1000,
        "end_ns": 2000,
        "duration_ms": 0.001,
        "attributes": MappingProxyType({"table": "users"}),
    }
    defaults.update(kwargs)
    return SpanRecord(**defaults)


@pytest.mark.pulse
class TestSnapshotLevelAware:
    def test_basic_spans_minimal(self):
        span = _make_span()
        rec = ExecutionRecord(
            correlation_id="c1", use_case_name="T", value_track="v",
            subtrack="", feature="", duration_ms=1.0, success=True,
            error_type="", spans=[span],
        )
        metrics = FakeMetricsCollector()
        snap = PulseSnapshot.from_records([rec], metrics, MonitoringLevel.BASIC, "0.3")
        s = snap.executions[0]["spans"][0]
        assert set(s.keys()) == {"span_id", "name", "duration_ms", "parent_span_id"}

    def test_detailed_spans_include_attributes(self):
        span = _make_span()
        rec = ExecutionRecord(
            correlation_id="c1", use_case_name="T", value_track="v",
            subtrack="", feature="", duration_ms=1.0, success=True,
            error_type="", spans=[span],
        )
        metrics = FakeMetricsCollector()
        snap = PulseSnapshot.from_records([rec], metrics, MonitoringLevel.DETAILED, "0.3")
        s = snap.executions[0]["spans"][0]
        assert "attributes" in s
        assert s["attributes"]["table"] == "users"
        assert "start_ns" not in s

    def test_diagnostic_spans_include_timing(self):
        span = _make_span(start_ns=100, end_ns=200)
        rec = ExecutionRecord(
            correlation_id="c1", use_case_name="T", value_track="v",
            subtrack="", feature="", duration_ms=1.0, success=True,
            error_type="", spans=[span],
        )
        metrics = FakeMetricsCollector()
        snap = PulseSnapshot.from_records([rec], metrics, MonitoringLevel.DIAGNOSTIC, "0.3")
        s = snap.executions[0]["spans"][0]
        assert s["start_ns"] == 100
        assert s["end_ns"] == 200
        assert "attributes" in s

    def test_detailed_tags_in_exec_dict(self):
        rec = ExecutionRecord(
            correlation_id="c1", use_case_name="T", value_track="v",
            subtrack="", feature="", duration_ms=1.0, success=True,
            error_type="", tags=MappingProxyType({"tier": "premium"}),
        )
        metrics = FakeMetricsCollector()
        snap = PulseSnapshot.from_records([rec], metrics, MonitoringLevel.DETAILED, "0.3")
        assert snap.executions[0]["tags"]["tier"] == "premium"

    def test_basic_no_tags_in_exec_dict(self):
        rec = ExecutionRecord(
            correlation_id="c1", use_case_name="T", value_track="v",
            subtrack="", feature="", duration_ms=1.0, success=True,
            error_type="", tags=MappingProxyType({"tier": "premium"}),
        )
        metrics = FakeMetricsCollector()
        snap = PulseSnapshot.from_records([rec], metrics, MonitoringLevel.BASIC, "0.3")
        assert "tags" not in snap.executions[0]

    def test_diagnostic_extra_in_exec_dict(self):
        rec = ExecutionRecord(
            correlation_id="c1", use_case_name="T", value_track="v",
            subtrack="", feature="", duration_ms=1.0, success=True,
            error_type="", extra=MappingProxyType({"debug": "1"}),
            mapping_source="spec",
        )
        metrics = FakeMetricsCollector()
        snap = PulseSnapshot.from_records([rec], metrics, MonitoringLevel.DIAGNOSTIC, "0.3")
        exec_dict = snap.executions[0]
        assert exec_dict["extra"]["debug"] == "1"
        assert exec_dict["mapping_source"] == "spec"

    def test_diagnostic_dropped_spans(self):
        rec = ExecutionRecord(
            correlation_id="c1", use_case_name="T", value_track="v",
            subtrack="", feature="", duration_ms=1.0, success=True,
            error_type="", dropped_spans=5,
        )
        metrics = FakeMetricsCollector()
        snap = PulseSnapshot.from_records([rec], metrics, MonitoringLevel.DIAGNOSTIC, "0.3")
        assert snap.executions[0]["dropped_spans"] == 5

    def test_diagnostic_no_dropped_when_zero(self):
        rec = ExecutionRecord(
            correlation_id="c1", use_case_name="T", value_track="v",
            subtrack="", feature="", duration_ms=1.0, success=True,
            error_type="", dropped_spans=0,
        )
        metrics = FakeMetricsCollector()
        snap = PulseSnapshot.from_records([rec], metrics, MonitoringLevel.DIAGNOSTIC, "0.3")
        assert "dropped_spans" not in snap.executions[0]


@pytest.mark.pulse
class TestHistogramStats:
    def test_fields(self):
        stats = HistogramStats(
            count=10,
            sum=100.0,
            mean=10.0,
            min=1.0,
            max=20.0,
            p50=9.0,
            p95=18.0,
            p99=19.0,
        )
        assert stats.count == 10
        assert stats.p95 == 18.0
