
import pytest

from forge_base.application.usecase_base import UseCaseBase
from forge_base.pulse.basic_collector import BasicCollector
from forge_base.pulse.budget import BudgetPolicy
from forge_base.pulse.context import _current_context, get_context
from forge_base.pulse.field_names import PulseFieldNames
from forge_base.pulse.level import MonitoringLevel
from forge_base.pulse.meta import pulse_meta
from forge_base.pulse.runner import UseCaseRunner
from forge_base.pulse.span import pulse_span
from forge_base.testing.fakes.fake_metrics_collector import FakeMetricsCollector


@pulse_meta(subtrack="checkout", feature="pay", tags={"tier": "premium", "region": "us"})
class _TaggedUseCase(UseCaseBase[str, str]):
    captured = None

    def _before_execute(self) -> None:
        pass

    def _after_execute(self) -> None:
        pass

    def _on_error(self, error: Exception) -> None:
        pass

    def execute(self, input_dto: str) -> str:
        self.__class__.captured = get_context()
        with pulse_span("db_call", table="users"):
            pass
        return input_dto


class _SpanningUseCase(UseCaseBase[str, str]):
    def _before_execute(self) -> None:
        pass

    def _after_execute(self) -> None:
        pass

    def _on_error(self, error: Exception) -> None:
        pass

    def execute(self, input_dto: str) -> str:
        with pulse_span("outer", kind="http"):
            with pulse_span("inner", detail="test"):
                pass
        return input_dto


class _ManySpansUseCase(UseCaseBase[str, str]):
    def __init__(self, count: int):
        self._count = count

    def _before_execute(self) -> None:
        pass

    def _after_execute(self) -> None:
        pass

    def _on_error(self, error: Exception) -> None:
        pass

    def execute(self, input_dto: str) -> str:
        for i in range(self._count):
            with pulse_span(f"span_{i}"):
                pass
        return input_dto


@pytest.mark.pulse
@pytest.mark.integration
class TestRunnerDetailedLevel:
    def setup_method(self):
        self._token = _current_context.set(None)
        _TaggedUseCase.captured = None

    def teardown_method(self):
        _current_context.reset(self._token)

    def test_tags_in_record(self):
        metrics = FakeMetricsCollector()
        collector = BasicCollector(metrics, level=MonitoringLevel.DETAILED)
        uc = _TaggedUseCase()
        runner = UseCaseRunner(uc, level=MonitoringLevel.DETAILED, collector=collector)
        runner.run("x")

        snap = collector.snapshot()
        exec_dict = snap.executions[0]
        assert "tags" in exec_dict
        assert exec_dict["tags"]["tier"] == "premium"
        assert exec_dict["tags"]["region"] == "us"

    def test_span_attrs_in_detailed_snapshot(self):
        metrics = FakeMetricsCollector()
        collector = BasicCollector(metrics, level=MonitoringLevel.DETAILED)
        uc = _SpanningUseCase()
        runner = UseCaseRunner(uc, level=MonitoringLevel.DETAILED, collector=collector)
        runner.run("x")

        snap = collector.snapshot()
        spans = snap.executions[0]["spans"]
        outer = next(s for s in spans if s["name"] == "outer")
        assert "attributes" in outer
        assert outer["attributes"]["kind"] == "http"

    def test_feature_in_detailed_metric_labels(self):
        metrics = FakeMetricsCollector()
        collector = BasicCollector(metrics, level=MonitoringLevel.DETAILED)
        uc = _TaggedUseCase()
        runner = UseCaseRunner(uc, level=MonitoringLevel.DETAILED, collector=collector)
        runner.run("x")

        assert metrics.was_incremented(
            PulseFieldNames.PULSE_EXEC_COUNT,
            use_case="_TaggedUseCase",
            value_track="legacy",
            subtrack="checkout",
            feature="pay",
        )

    def test_tags_not_in_basic_snapshot(self):
        metrics = FakeMetricsCollector()
        collector = BasicCollector(metrics, level=MonitoringLevel.BASIC)
        uc = _TaggedUseCase()
        runner = UseCaseRunner(uc, level=MonitoringLevel.BASIC, collector=collector)
        runner.run("x")

        snap = collector.snapshot()
        exec_dict = snap.executions[0]
        assert "tags" not in exec_dict

    def test_tags_runtime_override(self):
        metrics = FakeMetricsCollector()
        collector = BasicCollector(metrics, level=MonitoringLevel.DETAILED)
        uc = _TaggedUseCase()
        runner = UseCaseRunner(uc, level=MonitoringLevel.DETAILED, collector=collector)
        runner.run("x", tags={"tier": "free", "env": "staging"})

        ctx = _TaggedUseCase.captured
        assert ctx is not None
        assert ctx.tags["tier"] == "free"  # override wins
        assert ctx.tags["region"] == "us"  # meta base kept
        assert ctx.tags["env"] == "staging"  # new key added


@pytest.mark.pulse
@pytest.mark.integration
class TestRunnerDiagnosticLevel:
    def setup_method(self):
        self._token = _current_context.set(None)
        _TaggedUseCase.captured = None

    def teardown_method(self):
        _current_context.reset(self._token)

    def test_extra_in_diagnostic_record(self):
        metrics = FakeMetricsCollector()
        collector = BasicCollector(metrics, level=MonitoringLevel.DIAGNOSTIC)
        uc = _TaggedUseCase()
        runner = UseCaseRunner(uc, level=MonitoringLevel.DIAGNOSTIC, collector=collector)
        runner.run("x", extra={"debug_flag": "true"})

        snap = collector.snapshot()
        exec_dict = snap.executions[0]
        assert "extra" in exec_dict
        assert exec_dict["extra"]["debug_flag"] == "true"

    def test_mapping_source_in_diagnostic_snapshot(self):
        metrics = FakeMetricsCollector()
        collector = BasicCollector(metrics, level=MonitoringLevel.DIAGNOSTIC)
        uc = _TaggedUseCase()
        runner = UseCaseRunner(uc, level=MonitoringLevel.DIAGNOSTIC, collector=collector)
        runner.run("x")

        snap = collector.snapshot()
        exec_dict = snap.executions[0]
        assert "mapping_source" in exec_dict
        assert exec_dict["mapping_source"] == "decorator"

    def test_full_span_timing_in_diagnostic(self):
        metrics = FakeMetricsCollector()
        collector = BasicCollector(metrics, level=MonitoringLevel.DIAGNOSTIC)
        uc = _SpanningUseCase()
        runner = UseCaseRunner(uc, level=MonitoringLevel.DIAGNOSTIC, collector=collector)
        runner.run("x")

        snap = collector.snapshot()
        spans = snap.executions[0]["spans"]
        outer = next(s for s in spans if s["name"] == "outer")
        assert "start_ns" in outer
        assert "end_ns" in outer
        assert outer["end_ns"] > outer["start_ns"]

    def test_dropped_spans_in_diagnostic(self):
        metrics = FakeMetricsCollector()
        collector = BasicCollector(metrics, level=MonitoringLevel.DIAGNOSTIC)
        uc = _ManySpansUseCase(count=10)
        budget = BudgetPolicy(max_spans_per_execution=3)
        runner = UseCaseRunner(
            uc, level=MonitoringLevel.DIAGNOSTIC, collector=collector, budget=budget,
        )
        runner.run("x")

        snap = collector.snapshot()
        exec_dict = snap.executions[0]
        assert "dropped_spans" in exec_dict
        assert exec_dict["dropped_spans"] == 7

    def test_extra_not_in_detailed_snapshot(self):
        metrics = FakeMetricsCollector()
        collector = BasicCollector(metrics, level=MonitoringLevel.DETAILED)
        uc = _TaggedUseCase()
        runner = UseCaseRunner(uc, level=MonitoringLevel.DETAILED, collector=collector)
        runner.run("x", extra={"debug": "1"})

        snap = collector.snapshot()
        exec_dict = snap.executions[0]
        assert "extra" not in exec_dict


@pytest.mark.pulse
@pytest.mark.integration
class TestBackwardCompat:
    def setup_method(self):
        self._token = _current_context.set(None)

    def teardown_method(self):
        _current_context.reset(self._token)

    def test_basic_snapshot_unchanged(self):
        metrics = FakeMetricsCollector()
        collector = BasicCollector(metrics, level=MonitoringLevel.BASIC)
        uc = _SpanningUseCase()
        runner = UseCaseRunner(uc, level=MonitoringLevel.BASIC, collector=collector)
        runner.run("x")

        snap = collector.snapshot()
        exec_dict = snap.executions[0]
        spans = exec_dict["spans"]
        outer = next(s for s in spans if s["name"] == "outer")
        # BASIC spans have basic keys only
        assert set(outer.keys()) == {"span_id", "name", "duration_ms", "parent_span_id"}
        # No tags, extra, mapping_source, dropped_spans at BASIC
        assert "tags" not in exec_dict
        assert "extra" not in exec_dict
        assert "mapping_source" not in exec_dict
        assert "dropped_spans" not in exec_dict

    def test_standard_no_feature_metric(self):
        metrics = FakeMetricsCollector()
        collector = BasicCollector(metrics, level=MonitoringLevel.STANDARD)
        uc = _TaggedUseCase()
        runner = UseCaseRunner(uc, level=MonitoringLevel.STANDARD, collector=collector)
        runner.run("x")

        # STANDARD should NOT emit detailed labels with feature
        count = metrics.get_counter(
            PulseFieldNames.PULSE_EXEC_COUNT,
            use_case="_TaggedUseCase",
            value_track="legacy",
            subtrack="checkout",
            feature="pay",
        )
        assert count is None
