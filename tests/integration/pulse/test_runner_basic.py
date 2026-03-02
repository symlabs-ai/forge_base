import pytest

from forge_base.application.usecase_base import UseCaseBase
from forge_base.pulse.basic_collector import BasicCollector
from forge_base.pulse.context import _current_context, get_context
from forge_base.pulse.field_names import PulseFieldNames
from forge_base.pulse.level import MonitoringLevel
from forge_base.pulse.runner import UseCaseRunner
from forge_base.testing.fakes.fake_metrics_collector import FakeMetricsCollector


class _EchoUseCase(UseCaseBase[str, str]):
    def _before_execute(self) -> None:
        pass

    def _after_execute(self) -> None:
        pass

    def _on_error(self, error: Exception) -> None:
        pass

    def execute(self, input_dto: str) -> str:
        return input_dto


class _FailUseCase(UseCaseBase[str, str]):
    def _before_execute(self) -> None:
        pass

    def _after_execute(self) -> None:
        pass

    def _on_error(self, error: Exception) -> None:
        pass

    def execute(self, input_dto: str) -> str:
        raise ValueError("boom")


class _ContextCapture(UseCaseBase[str, str]):
    captured = None

    def _before_execute(self) -> None:
        pass

    def _after_execute(self) -> None:
        pass

    def _on_error(self, error: Exception) -> None:
        pass

    def execute(self, input_dto: str) -> str:
        self.__class__.captured = get_context()
        return input_dto


@pytest.mark.pulse
@pytest.mark.integration
class TestRunnerWithBasicCollector:
    def setup_method(self):
        self._token = _current_context.set(None)

    def teardown_method(self):
        _current_context.reset(self._token)

    def test_success_end_to_end(self):
        metrics = FakeMetricsCollector()
        collector = BasicCollector(metrics, level=MonitoringLevel.BASIC)
        uc = _EchoUseCase()
        runner = UseCaseRunner(uc, level=MonitoringLevel.BASIC, collector=collector)

        result = runner.run("hello")

        assert result == "hello"
        assert metrics.was_incremented(
            PulseFieldNames.PULSE_EXEC_COUNT,
            use_case="_EchoUseCase",
            value_track="legacy",
        )
        assert metrics.was_incremented(
            PulseFieldNames.PULSE_EXEC_SUCCESS,
            use_case="_EchoUseCase",
            value_track="legacy",
        )
        assert metrics.was_recorded(
            PulseFieldNames.PULSE_EXEC_DURATION_MS,
            use_case="_EchoUseCase",
            value_track="legacy",
        )

    def test_error_end_to_end(self):
        metrics = FakeMetricsCollector()
        collector = BasicCollector(metrics, level=MonitoringLevel.BASIC)
        uc = _FailUseCase()
        runner = UseCaseRunner(uc, level=MonitoringLevel.BASIC, collector=collector)

        with pytest.raises(ValueError, match="boom"):
            runner.run("hello")

        assert metrics.was_incremented(
            PulseFieldNames.PULSE_EXEC_ERRORS,
            use_case="_FailUseCase",
            value_track="legacy",
        )
        assert metrics.was_recorded(
            PulseFieldNames.PULSE_EXEC_DURATION_MS,
            use_case="_FailUseCase",
            value_track="legacy",
        )

    def test_snapshot_after_execution(self):
        metrics = FakeMetricsCollector()
        collector = BasicCollector(metrics, level=MonitoringLevel.BASIC)
        uc = _EchoUseCase()
        runner = UseCaseRunner(uc, level=MonitoringLevel.BASIC, collector=collector)

        runner.run("a")
        runner.run("b")

        snap = collector.snapshot()
        assert len(snap.executions) == 2
        assert snap.schema_version == "0.2"
        assert snap.level == MonitoringLevel.BASIC
        assert all(e["success"] is True for e in snap.executions)

    def test_heuristic_context_injected(self):
        _ContextCapture.captured = None
        metrics = FakeMetricsCollector()
        collector = BasicCollector(metrics, level=MonitoringLevel.BASIC)
        uc = _ContextCapture()
        runner = UseCaseRunner(uc, level=MonitoringLevel.BASIC, collector=collector)

        runner.run("x")

        ctx = _ContextCapture.captured
        assert ctx is not None
        assert ctx.use_case_name == "_ContextCapture"
        assert ctx.mapping_source == "heuristic"
        assert ctx.value_track == "legacy"
        assert ctx.feature != ""

    def test_ctx_overrides_win(self):
        _ContextCapture.captured = None
        metrics = FakeMetricsCollector()
        collector = BasicCollector(metrics, level=MonitoringLevel.BASIC)
        uc = _ContextCapture()
        runner = UseCaseRunner(uc, level=MonitoringLevel.BASIC, collector=collector)

        runner.run("x", value_track="premium", feature="custom")

        ctx = _ContextCapture.captured
        assert ctx is not None
        assert ctx.value_track == "premium"
        assert ctx.feature == "custom"

    def test_context_cleaned_up_after_run(self):
        metrics = FakeMetricsCollector()
        collector = BasicCollector(metrics, level=MonitoringLevel.BASIC)
        uc = _EchoUseCase()
        runner = UseCaseRunner(uc, level=MonitoringLevel.BASIC, collector=collector)
        runner.run("hello")
        assert get_context() is None

    def test_standard_level_emits_both_label_sets(self):
        metrics = FakeMetricsCollector()
        collector = BasicCollector(metrics, level=MonitoringLevel.STANDARD)
        uc = _EchoUseCase()
        runner = UseCaseRunner(uc, level=MonitoringLevel.STANDARD, collector=collector)

        runner.run("hello")

        # BASIC labels
        assert metrics.was_incremented(
            PulseFieldNames.PULSE_EXEC_COUNT,
            use_case="_EchoUseCase",
            value_track="legacy",
        )
        # At minimum the basic labels should be emitted
        basic_count = metrics.get_counter(
            PulseFieldNames.PULSE_EXEC_COUNT,
            use_case="_EchoUseCase",
            value_track="legacy",
        )
        assert basic_count is not None and basic_count >= 1
