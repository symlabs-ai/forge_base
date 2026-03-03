import pytest

from forge_base.application.usecase_base import UseCaseBase
from forge_base.pulse.basic_collector import BasicCollector
from forge_base.pulse.context import _current_context, get_context
from forge_base.pulse.level import MonitoringLevel
from forge_base.pulse.runner import UseCaseRunner
from forge_base.pulse.support_tracks import SupportTrackRegistry
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


def _make_spec():
    return {
        "schema_version": "0.2",
        "value_tracks": {
            "ProcessOrder": {
                "usecases": ["_EchoUseCase"],
            },
        },
        "support_tracks": {
            "ManageInventory": {
                "supports": ["ProcessOrder"],
                "usecases": ["_ContextCapture"],
                "description": "Inventory control",
                "tags": {"tier": "infra"},
            },
        },
    }


def _make_registries():
    spec = _make_spec()
    vreg = ValueTrackRegistry()
    vreg.load_from_dict(spec)
    sreg = SupportTrackRegistry()
    sreg.load_from_dict(spec)
    return vreg, sreg


@pytest.mark.pulse
@pytest.mark.integration
class TestRunnerWithSupportTracks:
    def setup_method(self):
        self._token = _current_context.set(None)
        _ContextCapture.captured = None

    def teardown_method(self):
        _current_context.reset(self._token)

    def test_support_registry_resolves_track_type(self):
        vreg, sreg = _make_registries()
        uc = _ContextCapture()
        runner = UseCaseRunner(
            uc, level=MonitoringLevel.BASIC, registry=vreg, support_registry=sreg,
        )
        runner.run("x")

        ctx = _ContextCapture.captured
        assert ctx is not None
        assert ctx.track_type == "support"
        assert ctx.value_track == "ManageInventory"
        assert ctx.subtrack == ""
        assert ctx.supports == ("ProcessOrder",)
        assert ctx.mapping_source == "spec"

    def test_value_registry_has_priority(self):
        """When a use case is in both value and support, value wins."""
        spec = {
            "schema_version": "0.2",
            "value_tracks": {
                "ProcessOrder": {
                    "usecases": ["_ContextCapture"],
                },
            },
            "support_tracks": {
                "ManageInventory": {
                    "supports": ["ProcessOrder"],
                    "usecases": ["_ContextCapture"],
                },
            },
        }
        vreg = ValueTrackRegistry()
        vreg.load_from_dict(spec)
        sreg = SupportTrackRegistry()
        sreg.load_from_dict(spec)

        uc = _ContextCapture()
        runner = UseCaseRunner(
            uc, level=MonitoringLevel.BASIC, registry=vreg, support_registry=sreg,
        )
        runner.run("x")

        ctx = _ContextCapture.captured
        assert ctx is not None
        # Value registry wins: track_type stays "value"
        assert ctx.track_type == "value"
        assert ctx.value_track == "ProcessOrder"

    def test_ctx_overrides_win_over_support_registry(self):
        vreg, sreg = _make_registries()
        uc = _ContextCapture()
        runner = UseCaseRunner(
            uc, level=MonitoringLevel.BASIC, registry=vreg, support_registry=sreg,
        )
        runner.run("x", track_type="value", value_track="custom")

        ctx = _ContextCapture.captured
        assert ctx is not None
        assert ctx.track_type == "value"
        assert ctx.value_track == "custom"

    def test_unmapped_defaults_to_value(self):
        sreg = SupportTrackRegistry()
        sreg.load_from_dict({
            "schema_version": "0.2",
            "value_tracks": {
                "ProcessOrder": {"usecases": ["Other"]},
            },
            "support_tracks": {
                "ManageInventory": {
                    "supports": ["ProcessOrder"],
                    "usecases": ["Other"],
                },
            },
        })

        uc = _ContextCapture()
        runner = UseCaseRunner(
            uc, level=MonitoringLevel.BASIC, support_registry=sreg,
        )
        runner.run("x")

        ctx = _ContextCapture.captured
        assert ctx is not None
        assert ctx.track_type == "value"
        assert ctx.supports == ()

    def test_support_track_record_in_collector(self):
        vreg, sreg = _make_registries()
        metrics = FakeMetricsCollector()
        collector = BasicCollector(metrics, level=MonitoringLevel.BASIC)
        uc = _ContextCapture()
        runner = UseCaseRunner(
            uc, level=MonitoringLevel.BASIC,
            collector=collector, registry=vreg, support_registry=sreg,
        )
        runner.run("x")

        snap = collector.snapshot()
        assert len(snap.executions) == 1
        exec_dict = snap.executions[0]
        assert exec_dict["track_type"] == "support"
        assert exec_dict["supports"] == ["ProcessOrder"]

    def test_no_support_registry_defaults(self):
        uc = _ContextCapture()
        runner = UseCaseRunner(uc, level=MonitoringLevel.BASIC)
        runner.run("x")

        ctx = _ContextCapture.captured
        assert ctx is not None
        assert ctx.track_type == "value"
        assert ctx.supports == ()
