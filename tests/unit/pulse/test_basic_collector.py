import pytest

from forge_base.pulse.basic_collector import BasicCollector, ExecutionRecord
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
