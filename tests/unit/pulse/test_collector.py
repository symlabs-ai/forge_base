import pytest

from forge_base.pulse.collector import NoOpCollector, PulseCollector
from forge_base.pulse.context import ExecutionContext


@pytest.mark.pulse
class TestNoOpCollector:
    def test_satisfies_protocol(self):
        collector = NoOpCollector()
        assert isinstance(collector, PulseCollector)

    def test_on_start_is_noop(self):
        collector = NoOpCollector()
        ctx = ExecutionContext(correlation_id="abc")
        collector.on_start(ctx)  # no error

    def test_on_success_is_noop(self):
        collector = NoOpCollector()
        ctx = ExecutionContext(correlation_id="abc")
        collector.on_success(ctx, "result")  # no error

    def test_on_error_is_noop(self):
        collector = NoOpCollector()
        ctx = ExecutionContext(correlation_id="abc")
        collector.on_error(ctx, RuntimeError("boom"))  # no error

    def test_on_finish_is_noop(self):
        collector = NoOpCollector()
        ctx = ExecutionContext(correlation_id="abc")
        collector.on_finish(ctx)  # no error
