from types import MappingProxyType

import pytest

from forge_base.pulse.basic_collector import _EMPTY_TAGS, BasicCollector, ExecutionRecord
from forge_base.pulse.context import ExecutionContext
from forge_base.pulse.field_names import PulseFieldNames
from forge_base.pulse.level import MonitoringLevel
from forge_base.testing.fakes.fake_metrics_collector import FakeMetricsCollector


def _make_ctx(
    cid: str = "test-123",
    level: MonitoringLevel = MonitoringLevel.BASIC,
    use_case_name: str = "TestUseCase",
    value_track: str = "legacy",
    subtrack: str = "billing",
    feature: str = "create_invoice",
) -> ExecutionContext:
    return ExecutionContext.build(
        correlation_id=cid,
        level=level,
        use_case_name=use_case_name,
        value_track=value_track,
        subtrack=subtrack,
        feature=feature,
    )


@pytest.mark.pulse
class TestBasicCollectorBasicLevel:
    def test_on_start_increments_count(self):
        metrics = FakeMetricsCollector()
        collector = BasicCollector(metrics, level=MonitoringLevel.BASIC)
        ctx = _make_ctx()
        collector.on_start(ctx)
        assert metrics.was_incremented(
            PulseFieldNames.PULSE_EXEC_COUNT,
            use_case="TestUseCase",
            value_track="legacy",
        )

    def test_on_success_increments_success(self):
        metrics = FakeMetricsCollector()
        collector = BasicCollector(metrics, level=MonitoringLevel.BASIC)
        ctx = _make_ctx()
        collector.on_start(ctx)
        collector.on_success(ctx, "result")
        assert metrics.was_incremented(
            PulseFieldNames.PULSE_EXEC_SUCCESS,
            use_case="TestUseCase",
            value_track="legacy",
        )

    def test_on_error_increments_errors(self):
        metrics = FakeMetricsCollector()
        collector = BasicCollector(metrics, level=MonitoringLevel.BASIC)
        ctx = _make_ctx()
        collector.on_start(ctx)
        collector.on_error(ctx, ValueError("boom"))
        assert metrics.was_incremented(
            PulseFieldNames.PULSE_EXEC_ERRORS,
            use_case="TestUseCase",
            value_track="legacy",
        )

    def test_on_finish_records_duration(self):
        metrics = FakeMetricsCollector()
        collector = BasicCollector(metrics, level=MonitoringLevel.BASIC)
        ctx = _make_ctx()
        collector.on_start(ctx)
        collector.on_success(ctx, "ok")
        collector.on_finish(ctx)
        assert metrics.was_recorded(
            PulseFieldNames.PULSE_EXEC_DURATION_MS,
            use_case="TestUseCase",
            value_track="legacy",
        )

    def test_on_finish_creates_record(self):
        metrics = FakeMetricsCollector()
        collector = BasicCollector(metrics, level=MonitoringLevel.BASIC)
        ctx = _make_ctx()
        collector.on_start(ctx)
        collector.on_success(ctx, "ok")
        collector.on_finish(ctx)
        snap = collector.snapshot()
        assert len(snap.executions) == 1
        rec = snap.executions[0]
        assert rec["use_case_name"] == "TestUseCase"
        assert rec["success"] is True
        assert rec["error_type"] == ""

    def test_error_record_has_error_type(self):
        metrics = FakeMetricsCollector()
        collector = BasicCollector(metrics, level=MonitoringLevel.BASIC)
        ctx = _make_ctx()
        collector.on_start(ctx)
        collector.on_error(ctx, ValueError("boom"))
        collector.on_finish(ctx)
        snap = collector.snapshot()
        rec = snap.executions[0]
        assert rec["success"] is False
        assert rec["error_type"] == "ValueError"

    def test_clear_records(self):
        metrics = FakeMetricsCollector()
        collector = BasicCollector(metrics, level=MonitoringLevel.BASIC)
        ctx = _make_ctx()
        collector.on_start(ctx)
        collector.on_success(ctx, "ok")
        collector.on_finish(ctx)
        assert len(collector.snapshot().executions) == 1
        collector.clear_records()
        assert len(collector.snapshot().executions) == 0

    def test_basic_does_not_emit_standard_labels(self):
        metrics = FakeMetricsCollector()
        collector = BasicCollector(metrics, level=MonitoringLevel.BASIC)
        ctx = _make_ctx()
        collector.on_start(ctx)
        # Should NOT have counter with subtrack label
        count = metrics.get_counter(
            PulseFieldNames.PULSE_EXEC_COUNT,
            use_case="TestUseCase",
            value_track="legacy",
            subtrack="billing",
        )
        assert count is None


@pytest.mark.pulse
class TestBasicCollectorStandardLevel:
    def test_standard_emits_both_label_sets(self):
        metrics = FakeMetricsCollector()
        collector = BasicCollector(metrics, level=MonitoringLevel.STANDARD)
        ctx = _make_ctx()
        collector.on_start(ctx)

        # BASIC labels
        assert metrics.was_incremented(
            PulseFieldNames.PULSE_EXEC_COUNT,
            use_case="TestUseCase",
            value_track="legacy",
        )
        # STANDARD labels
        assert metrics.was_incremented(
            PulseFieldNames.PULSE_EXEC_COUNT,
            use_case="TestUseCase",
            value_track="legacy",
            subtrack="billing",
        )

    def test_standard_duration_both_label_sets(self):
        metrics = FakeMetricsCollector()
        collector = BasicCollector(metrics, level=MonitoringLevel.STANDARD)
        ctx = _make_ctx()
        collector.on_start(ctx)
        collector.on_success(ctx, "ok")
        collector.on_finish(ctx)

        assert metrics.was_recorded(
            PulseFieldNames.PULSE_EXEC_DURATION_MS,
            use_case="TestUseCase",
            value_track="legacy",
        )
        assert metrics.was_recorded(
            PulseFieldNames.PULSE_EXEC_DURATION_MS,
            use_case="TestUseCase",
            value_track="legacy",
            subtrack="billing",
        )


@pytest.mark.pulse
class TestBasicCollectorDetailedLevel:
    def test_detailed_emits_feature_labels(self):
        metrics = FakeMetricsCollector()
        collector = BasicCollector(metrics, level=MonitoringLevel.DETAILED)
        ctx = _make_ctx()
        collector.on_start(ctx)

        assert metrics.was_incremented(
            PulseFieldNames.PULSE_EXEC_COUNT,
            use_case="TestUseCase",
            value_track="legacy",
            subtrack="billing",
            feature="create_invoice",
        )

    def test_detailed_emits_basic_and_standard_too(self):
        metrics = FakeMetricsCollector()
        collector = BasicCollector(metrics, level=MonitoringLevel.DETAILED)
        ctx = _make_ctx()
        collector.on_start(ctx)

        assert metrics.was_incremented(
            PulseFieldNames.PULSE_EXEC_COUNT,
            use_case="TestUseCase",
            value_track="legacy",
        )
        assert metrics.was_incremented(
            PulseFieldNames.PULSE_EXEC_COUNT,
            use_case="TestUseCase",
            value_track="legacy",
            subtrack="billing",
        )

    def test_detailed_success_feature_labels(self):
        metrics = FakeMetricsCollector()
        collector = BasicCollector(metrics, level=MonitoringLevel.DETAILED)
        ctx = _make_ctx()
        collector.on_start(ctx)
        collector.on_success(ctx, "ok")

        assert metrics.was_incremented(
            PulseFieldNames.PULSE_EXEC_SUCCESS,
            use_case="TestUseCase",
            value_track="legacy",
            subtrack="billing",
            feature="create_invoice",
        )

    def test_detailed_error_feature_labels(self):
        metrics = FakeMetricsCollector()
        collector = BasicCollector(metrics, level=MonitoringLevel.DETAILED)
        ctx = _make_ctx()
        collector.on_start(ctx)
        collector.on_error(ctx, ValueError("boom"))

        assert metrics.was_incremented(
            PulseFieldNames.PULSE_EXEC_ERRORS,
            use_case="TestUseCase",
            value_track="legacy",
            subtrack="billing",
            feature="create_invoice",
        )

    def test_detailed_duration_feature_labels(self):
        metrics = FakeMetricsCollector()
        collector = BasicCollector(metrics, level=MonitoringLevel.DETAILED)
        ctx = _make_ctx()
        collector.on_start(ctx)
        collector.on_success(ctx, "ok")
        collector.on_finish(ctx)

        assert metrics.was_recorded(
            PulseFieldNames.PULSE_EXEC_DURATION_MS,
            use_case="TestUseCase",
            value_track="legacy",
            subtrack="billing",
            feature="create_invoice",
        )

    def test_detailed_record_has_tags(self):
        metrics = FakeMetricsCollector()
        collector = BasicCollector(metrics, level=MonitoringLevel.DETAILED)
        ctx = ExecutionContext.build(
            correlation_id="t1",
            level=MonitoringLevel.DETAILED,
            use_case_name="Test",
            tags={"tier": "premium"},
        )
        collector.on_start(ctx)
        collector.on_success(ctx, "ok")
        collector.on_finish(ctx)

        snap = collector.snapshot()
        assert snap.executions[0]["tags"]["tier"] == "premium"

    def test_basic_record_no_tags(self):
        metrics = FakeMetricsCollector()
        collector = BasicCollector(metrics, level=MonitoringLevel.BASIC)
        ctx = ExecutionContext.build(
            correlation_id="t1",
            level=MonitoringLevel.BASIC,
            use_case_name="Test",
            tags={"tier": "premium"},
        )
        collector.on_start(ctx)
        collector.on_success(ctx, "ok")
        collector.on_finish(ctx)

        snap = collector.snapshot()
        assert "tags" not in snap.executions[0]

    def test_diagnostic_record_has_extra(self):
        metrics = FakeMetricsCollector()
        collector = BasicCollector(metrics, level=MonitoringLevel.DIAGNOSTIC)
        ctx = ExecutionContext.build(
            correlation_id="t1",
            level=MonitoringLevel.DIAGNOSTIC,
            use_case_name="Test",
            extra={"debug": "1"},
            mapping_source="spec",
        )
        collector.on_start(ctx)
        collector.on_success(ctx, "ok")
        collector.on_finish(ctx)

        snap = collector.snapshot()
        exec_dict = snap.executions[0]
        assert "extra" in exec_dict
        assert exec_dict["extra"]["debug"] == "1"
        assert exec_dict["mapping_source"] == "spec"


@pytest.mark.pulse
class TestExecutionRecord:
    def test_dataclass_fields(self):
        rec = ExecutionRecord(
            correlation_id="abc",
            use_case_name="Test",
            value_track="legacy",
            subtrack="billing",
            feature="create",
            duration_ms=1.5,
            success=True,
            error_type="",
        )
        assert rec.correlation_id == "abc"
        assert rec.duration_ms == 1.5
        assert rec.success is True
        assert rec.timestamp > 0

    def test_new_fields_defaults(self):
        rec = ExecutionRecord(
            correlation_id="abc",
            use_case_name="Test",
            value_track="legacy",
            subtrack="",
            feature="",
            duration_ms=1.0,
            success=True,
            error_type="",
        )
        assert rec.tags == _EMPTY_TAGS
        assert len(rec.extra) == 0
        assert rec.mapping_source == ""
        assert rec.dropped_spans == 0

    def test_new_fields_populated(self):
        rec = ExecutionRecord(
            correlation_id="abc",
            use_case_name="Test",
            value_track="legacy",
            subtrack="",
            feature="",
            duration_ms=1.0,
            success=True,
            error_type="",
            tags=MappingProxyType({"tier": "premium"}),
            extra=MappingProxyType({"debug": "1"}),
            mapping_source="spec",
            dropped_spans=3,
        )
        assert rec.tags["tier"] == "premium"
        assert rec.extra["debug"] == "1"
        assert rec.mapping_source == "spec"
        assert rec.dropped_spans == 3

    def test_track_type_default(self):
        rec = ExecutionRecord(
            correlation_id="abc",
            use_case_name="Test",
            value_track="legacy",
            subtrack="",
            feature="",
            duration_ms=1.0,
            success=True,
            error_type="",
        )
        assert rec.track_type == "value"
        assert rec.supports == ()

    def test_track_type_support(self):
        rec = ExecutionRecord(
            correlation_id="abc",
            use_case_name="Test",
            value_track="ManageInventory",
            subtrack="",
            feature="",
            duration_ms=1.0,
            success=True,
            error_type="",
            track_type="support",
            supports=("ProcessOrder",),
        )
        assert rec.track_type == "support"
        assert rec.supports == ("ProcessOrder",)


@pytest.mark.pulse
class TestBasicCollectorTrackTypePropagation:
    def test_support_track_propagated_to_record(self):
        metrics = FakeMetricsCollector()
        collector = BasicCollector(metrics, level=MonitoringLevel.BASIC)
        ctx = ExecutionContext.build(
            correlation_id="t1",
            level=MonitoringLevel.BASIC,
            use_case_name="SyncInventory",
            value_track="ManageInventory",
            track_type="support",
            supports=("ProcessOrder",),
        )
        collector.on_start(ctx)
        collector.on_success(ctx, "ok")
        collector.on_finish(ctx)

        snap = collector.snapshot()
        exec_dict = snap.executions[0]
        assert exec_dict["track_type"] == "support"
        assert exec_dict["supports"] == ["ProcessOrder"]

    def test_value_track_default_in_record(self):
        metrics = FakeMetricsCollector()
        collector = BasicCollector(metrics, level=MonitoringLevel.BASIC)
        ctx = _make_ctx()
        collector.on_start(ctx)
        collector.on_success(ctx, "ok")
        collector.on_finish(ctx)

        snap = collector.snapshot()
        exec_dict = snap.executions[0]
        assert exec_dict["track_type"] == "value"
        assert "supports" not in exec_dict
