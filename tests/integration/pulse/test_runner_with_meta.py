import pytest

from forge_base.application.usecase_base import UseCaseBase
from forge_base.pulse.basic_collector import BasicCollector
from forge_base.pulse.context import _current_context, get_context
from forge_base.pulse.field_names import PulseFieldNames
from forge_base.pulse.level import MonitoringLevel
from forge_base.pulse.meta import pulse_meta, read_pulse_meta
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


@pulse_meta(subtrack="checkout", feature="pay", value_track="revenue")
class _DecoratedCapture(UseCaseBase[str, str]):
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


@pulse_meta(subtrack="partial_sub")
class _PartialDecoratedCapture(UseCaseBase[str, str]):
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


@pulse_meta(subtrack="checkout", tags={"tier": "premium"})
class _TaggedCapture(UseCaseBase[str, str]):
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


def _make_registry(*use_case_names):
    reg = ValueTrackRegistry()
    reg.load_from_dict({
        "schema_version": "0.1",
        "value_tracks": {
            "spec_track": {
                "usecases": list(use_case_names),
                "subtracks": {"spec_sub": list(use_case_names)},
            },
        },
    })
    return reg


@pytest.mark.pulse
@pytest.mark.integration
class TestRunnerWithMeta:
    def setup_method(self):
        self._token = _current_context.set(None)
        _ContextCapture.captured = None
        _DecoratedCapture.captured = None
        _PartialDecoratedCapture.captured = None
        _TaggedCapture.captured = None

    def teardown_method(self):
        _current_context.reset(self._token)

    def test_decorator_overrides_heuristic(self):
        """Layer 2 > Layer 1: decorator wins over heuristic."""
        uc = _DecoratedCapture()
        runner = UseCaseRunner(uc, level=MonitoringLevel.BASIC)
        runner.run("x")

        ctx = _DecoratedCapture.captured
        assert ctx is not None
        assert ctx.value_track == "revenue"
        assert ctx.subtrack == "checkout"
        assert ctx.feature == "pay"
        assert ctx.mapping_source == "decorator"

    def test_partial_decorator_keeps_heuristic_value_track(self):
        """Layer 2 partial: subtrack from decorator, value_track stays 'legacy'."""
        uc = _PartialDecoratedCapture()
        runner = UseCaseRunner(uc, level=MonitoringLevel.BASIC)
        runner.run("x")

        ctx = _PartialDecoratedCapture.captured
        assert ctx is not None
        assert ctx.subtrack == "partial_sub"
        assert ctx.value_track == "legacy"
        assert ctx.mapping_source == "decorator"

    def test_registry_overrides_decorator(self):
        """Layer 3 > Layer 2: registry wins over decorator."""
        reg = _make_registry("_DecoratedCapture")
        uc = _DecoratedCapture()
        runner = UseCaseRunner(uc, level=MonitoringLevel.BASIC, registry=reg)
        runner.run("x")

        ctx = _DecoratedCapture.captured
        assert ctx is not None
        assert ctx.value_track == "spec_track"
        assert ctx.subtrack == "spec_sub"
        assert ctx.mapping_source == "spec"

    def test_ctx_overrides_win_over_everything(self):
        """Layer 4 > all: per-call ctx_overrides win."""
        reg = _make_registry("_DecoratedCapture")
        uc = _DecoratedCapture()
        runner = UseCaseRunner(uc, level=MonitoringLevel.BASIC, registry=reg)
        runner.run("x", value_track="override_track", subtrack="override_sub")

        ctx = _DecoratedCapture.captured
        assert ctx is not None
        assert ctx.value_track == "override_track"
        assert ctx.subtrack == "override_sub"

    def test_plain_usecase_no_decorator_no_registry(self):
        """Backward compat: plain usecase without decorator or registry."""
        uc = _ContextCapture()
        runner = UseCaseRunner(uc, level=MonitoringLevel.BASIC)
        runner.run("x")

        ctx = _ContextCapture.captured
        assert ctx is not None
        assert ctx.value_track == "legacy"
        assert ctx.mapping_source == "heuristic"

    def test_decorator_with_basic_collector(self):
        """Decorator value_track flows into BasicCollector metrics."""
        metrics = FakeMetricsCollector()
        collector = BasicCollector(metrics, level=MonitoringLevel.BASIC)
        uc = _DecoratedCapture()
        runner = UseCaseRunner(uc, level=MonitoringLevel.BASIC, collector=collector)
        runner.run("hello")

        assert metrics.was_incremented(
            PulseFieldNames.PULSE_EXEC_COUNT,
            use_case="_DecoratedCapture",
            value_track="revenue",
        )

    def test_tags_available_via_read_pulse_meta(self):
        """Tags stored on decorator, accessible via read_pulse_meta."""
        uc = _TaggedCapture()
        meta = read_pulse_meta(uc)
        assert meta is not None
        assert meta.tags["tier"] == "premium"

    def test_tags_not_propagated_to_ctx_extra(self):
        """Tags are NOT propagated to ExecutionContext.extra (Fase 4)."""
        uc = _TaggedCapture()
        runner = UseCaseRunner(uc, level=MonitoringLevel.BASIC)
        runner.run("x")

        ctx = _TaggedCapture.captured
        assert ctx is not None
        assert "tier" not in ctx.extra

    def test_schema_version_unchanged(self):
        """Schema version stays 0.3 — wire format unchanged."""
        metrics = FakeMetricsCollector()
        collector = BasicCollector(metrics, level=MonitoringLevel.BASIC)
        uc = _DecoratedCapture()
        runner = UseCaseRunner(uc, level=MonitoringLevel.BASIC, collector=collector)
        runner.run("x")
        snap = collector.snapshot()
        assert snap.schema_version == "0.3"

    def test_off_level_with_decorator(self):
        """OFF level ignores decorator entirely."""
        uc = _DecoratedCapture()
        runner = UseCaseRunner(uc, level=MonitoringLevel.OFF)
        result = runner.run("hello")
        assert result == "hello"
        assert runner._inferred == {}
