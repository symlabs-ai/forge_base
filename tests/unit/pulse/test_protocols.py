import pytest

from forge_base.pulse.protocols import PulseMetricsProtocol


@pytest.mark.pulse
class TestPulseMetricsProtocol:
    def test_track_metrics_satisfies(self):
        from forge_base.observability.track_metrics import TrackMetrics

        metrics = TrackMetrics()
        assert isinstance(metrics, PulseMetricsProtocol)

    def test_fake_metrics_collector_satisfies(self):
        from forge_base.testing.fakes.fake_metrics_collector import FakeMetricsCollector

        metrics = FakeMetricsCollector()
        assert isinstance(metrics, PulseMetricsProtocol)

    def test_arbitrary_class_does_not_satisfy(self):
        class NotMetrics:
            pass

        assert not isinstance(NotMetrics(), PulseMetricsProtocol)
