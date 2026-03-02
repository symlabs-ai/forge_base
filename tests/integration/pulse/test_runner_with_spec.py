import pytest

from forge_base.application.usecase_base import UseCaseBase
from forge_base.pulse.basic_collector import BasicCollector
from forge_base.pulse.context import _current_context, get_context
from forge_base.pulse.field_names import PulseFieldNames
from forge_base.pulse.level import MonitoringLevel
from forge_base.pulse.runner import UseCaseRunner
from forge_base.pulse.value_tracks import ValueTrackRegistry
from forge_base.testing.fakes.fake_metrics_collector import FakeMetricsCollector


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


class _EchoUseCase(UseCaseBase[str, str]):
    def _before_execute(self) -> None:
        pass

    def _after_execute(self) -> None:
        pass

    def _on_error(self, error: Exception) -> None:
        pass

    def execute(self, input_dto: str) -> str:
        return input_dto


def _make_registry():
    reg = ValueTrackRegistry()
    reg.load_from_dict({
        "schema_version": "0.1",
        "value_tracks": {
            "revenue": {
                "usecases": ["_ContextCapture", "_EchoUseCase"],
                "subtracks": {"checkout": ["_ContextCapture"]},
                "tags": {"tier": "premium"},
            },
        },
    })
    return reg


@pytest.mark.pulse
@pytest.mark.integration
class TestRunnerWithSpec:
    def setup_method(self):
        self._token = _current_context.set(None)
        _ContextCapture.captured = None

    def teardown_method(self):
        _current_context.reset(self._token)

    def test_registry_overrides_heuristic(self):
        reg = _make_registry()
        uc = _ContextCapture()
        runner = UseCaseRunner(uc, level=MonitoringLevel.BASIC, registry=reg)
        runner.run("x")

        ctx = _ContextCapture.captured
        assert ctx is not None
        assert ctx.value_track == "revenue"
        assert ctx.subtrack == "checkout"
        assert ctx.mapping_source == "spec"

    def test_ctx_overrides_win_over_registry(self):
        reg = _make_registry()
        uc = _ContextCapture()
        runner = UseCaseRunner(uc, level=MonitoringLevel.BASIC, registry=reg)
        runner.run("x", value_track="custom", subtrack="override")

        ctx = _ContextCapture.captured
        assert ctx is not None
        assert ctx.value_track == "custom"
        assert ctx.subtrack == "override"

    def test_unmapped_usecase_keeps_heuristic(self):
        reg = ValueTrackRegistry()
        reg.load_from_dict({
            "schema_version": "0.1",
            "value_tracks": {
                "revenue": {"usecases": ["SomeOtherUseCase"]},
            },
        })
        uc = _ContextCapture()
        runner = UseCaseRunner(uc, level=MonitoringLevel.BASIC, registry=reg)
        runner.run("x")

        ctx = _ContextCapture.captured
        assert ctx is not None
        assert ctx.value_track == "legacy"
        assert ctx.mapping_source == "heuristic"

    def test_no_registry_keeps_heuristic(self):
        uc = _ContextCapture()
        runner = UseCaseRunner(uc, level=MonitoringLevel.BASIC)
        runner.run("x")

        ctx = _ContextCapture.captured
        assert ctx is not None
        assert ctx.value_track == "legacy"
        assert ctx.mapping_source == "heuristic"

    def test_registry_with_basic_collector(self):
        reg = _make_registry()
        metrics = FakeMetricsCollector()
        collector = BasicCollector(metrics, level=MonitoringLevel.BASIC)
        uc = _EchoUseCase()
        runner = UseCaseRunner(
            uc, level=MonitoringLevel.BASIC, collector=collector, registry=reg,
        )
        result = runner.run("hello")

        assert result == "hello"
        assert metrics.was_incremented(
            PulseFieldNames.PULSE_EXEC_COUNT,
            use_case="_EchoUseCase",
            value_track="revenue",
        )

    def test_registry_from_yaml(self, tmp_path):
        yaml_content = (
            "schema_version: '0.1'\n"
            "value_tracks:\n"
            "  revenue:\n"
            "    usecases:\n"
            "      - _ContextCapture\n"
        )
        p = tmp_path / "spec.yaml"
        p.write_text(yaml_content)

        reg = ValueTrackRegistry()
        reg.load_from_yaml(p)

        uc = _ContextCapture()
        runner = UseCaseRunner(uc, level=MonitoringLevel.BASIC, registry=reg)
        runner.run("x")

        ctx = _ContextCapture.captured
        assert ctx is not None
        assert ctx.value_track == "revenue"

    def test_off_level_ignores_registry(self):
        reg = _make_registry()
        uc = _EchoUseCase()
        runner = UseCaseRunner(uc, level=MonitoringLevel.OFF, registry=reg)
        result = runner.run("hello")
        assert result == "hello"

    def test_schema_version_updated(self):
        metrics = FakeMetricsCollector()
        collector = BasicCollector(metrics, level=MonitoringLevel.BASIC)
        reg = _make_registry()
        uc = _EchoUseCase()
        runner = UseCaseRunner(
            uc, level=MonitoringLevel.BASIC, collector=collector, registry=reg,
        )
        runner.run("hello")
        snap = collector.snapshot()
        assert snap.schema_version == "0.3"
