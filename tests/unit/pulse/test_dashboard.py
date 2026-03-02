import pytest

from forge_base.pulse.dashboard import DashboardSummary, TrackSummary, _percentile
from forge_base.pulse.level import MonitoringLevel
from forge_base.pulse.report import PulseSnapshot


def _make_snapshot(executions=None, level=MonitoringLevel.BASIC):
    return PulseSnapshot(
        timestamp=1000.0,
        schema_version="0.3",
        level=level,
        executions=executions or [],
        counters={},
        histograms={},
    )


def _exec(
    success=True,
    duration_ms=10.0,
    value_track="core",
    error_type="",
    use_case_name="TestUC",
):
    return {
        "correlation_id": "cid",
        "use_case_name": use_case_name,
        "value_track": value_track,
        "subtrack": "",
        "feature": "",
        "duration_ms": duration_ms,
        "success": success,
        "error_type": error_type,
        "timestamp": 1000.0,
    }


@pytest.mark.pulse
class TestDashboardSummaryEmpty:
    def test_empty_snapshot_all_zeros(self):
        snap = _make_snapshot()
        ds = DashboardSummary.from_snapshot(snap)
        assert ds.total_executions == 0
        assert ds.successful == 0
        assert ds.failed == 0
        assert ds.error_rate == 0.0
        assert ds.mean_duration_ms == 0.0
        assert ds.top_error_types == ()
        assert ds.by_value_track == ()


@pytest.mark.pulse
class TestDashboardSummaryBasic:
    def test_total_and_success_count(self):
        execs = [_exec(success=True), _exec(success=True), _exec(success=False, error_type="Err")]
        snap = _make_snapshot(execs)
        ds = DashboardSummary.from_snapshot(snap)
        assert ds.total_executions == 3
        assert ds.successful == 2
        assert ds.failed == 1

    def test_error_rate(self):
        execs = [_exec(success=True), _exec(success=False, error_type="E")]
        snap = _make_snapshot(execs)
        ds = DashboardSummary.from_snapshot(snap)
        assert ds.error_rate == pytest.approx(0.5)

    def test_mean_duration(self):
        execs = [_exec(duration_ms=10.0), _exec(duration_ms=20.0), _exec(duration_ms=30.0)]
        snap = _make_snapshot(execs)
        ds = DashboardSummary.from_snapshot(snap)
        assert ds.mean_duration_ms == pytest.approx(20.0)

    def test_top_error_types(self):
        execs = [
            _exec(success=False, error_type="ValueError"),
            _exec(success=False, error_type="ValueError"),
            _exec(success=False, error_type="TypeError"),
            _exec(success=True),
        ]
        snap = _make_snapshot(execs)
        ds = DashboardSummary.from_snapshot(snap)
        assert ds.top_error_types[0] == ("ValueError", 2)
        assert ds.top_error_types[1] == ("TypeError", 1)

    def test_by_value_track(self):
        execs = [
            _exec(value_track="billing", duration_ms=10.0),
            _exec(value_track="billing", duration_ms=20.0),
            _exec(value_track="search", duration_ms=5.0),
        ]
        snap = _make_snapshot(execs)
        ds = DashboardSummary.from_snapshot(snap)
        assert len(ds.by_value_track) == 2
        # sorted by name
        assert ds.by_value_track[0].value_track == "billing"
        assert ds.by_value_track[1].value_track == "search"

    def test_by_value_track_counts(self):
        execs = [
            _exec(value_track="billing", success=True),
            _exec(value_track="billing", success=False, error_type="E"),
        ]
        snap = _make_snapshot(execs)
        ds = DashboardSummary.from_snapshot(snap)
        billing = ds.by_value_track[0]
        assert billing.total_executions == 2
        assert billing.successful == 1
        assert billing.failed == 1
        assert billing.error_rate == pytest.approx(0.5)


@pytest.mark.pulse
class TestTrackSummary:
    def test_error_rate_calculation(self):
        ts = TrackSummary(
            value_track="core",
            total_executions=10,
            successful=7,
            failed=3,
            error_rate=0.3,
            mean_duration_ms=15.0,
            p95_duration_ms=25.0,
        )
        assert ts.error_rate == pytest.approx(0.3)

    def test_p95_via_from_snapshot(self):
        execs = [_exec(duration_ms=float(i)) for i in range(1, 101)]
        snap = _make_snapshot(execs)
        ds = DashboardSummary.from_snapshot(snap)
        track = ds.by_value_track[0]
        assert track.p95_duration_ms >= 95.0


@pytest.mark.pulse
class TestDashboardSummaryFrozen:
    def test_frozen_dashboard(self):
        snap = _make_snapshot([_exec()])
        ds = DashboardSummary.from_snapshot(snap)
        with pytest.raises(AttributeError):
            ds.total_executions = 99  # type: ignore[misc]

    def test_frozen_track_summary(self):
        snap = _make_snapshot([_exec()])
        ds = DashboardSummary.from_snapshot(snap)
        with pytest.raises(AttributeError):
            ds.by_value_track[0].total_executions = 99  # type: ignore[misc]

    def test_top_error_types_is_tuple(self):
        snap = _make_snapshot([_exec(success=False, error_type="E")])
        ds = DashboardSummary.from_snapshot(snap)
        assert isinstance(ds.top_error_types, tuple)

    def test_by_value_track_is_tuple(self):
        snap = _make_snapshot([_exec()])
        ds = DashboardSummary.from_snapshot(snap)
        assert isinstance(ds.by_value_track, tuple)


@pytest.mark.pulse
class TestDashboardSummaryEdgeCases:
    def test_all_success(self):
        execs = [_exec(success=True) for _ in range(5)]
        snap = _make_snapshot(execs)
        ds = DashboardSummary.from_snapshot(snap)
        assert ds.failed == 0
        assert ds.error_rate == 0.0
        assert ds.top_error_types == ()

    def test_all_fail(self):
        execs = [_exec(success=False, error_type="E") for _ in range(5)]
        snap = _make_snapshot(execs)
        ds = DashboardSummary.from_snapshot(snap)
        assert ds.successful == 0
        assert ds.error_rate == 1.0

    def test_single_execution(self):
        snap = _make_snapshot([_exec(duration_ms=42.0)])
        ds = DashboardSummary.from_snapshot(snap)
        assert ds.total_executions == 1
        assert ds.mean_duration_ms == 42.0

    def test_top_n_greater_than_actual_errors(self):
        execs = [_exec(success=False, error_type="OnlyError")]
        snap = _make_snapshot(execs)
        ds = DashboardSummary.from_snapshot(snap, top_n=10)
        assert len(ds.top_error_types) == 1
        assert ds.top_error_types[0] == ("OnlyError", 1)


@pytest.mark.pulse
class TestPercentile:
    def test_empty_returns_zero(self):
        assert _percentile([], 95) == 0.0

    def test_single_value(self):
        assert _percentile([10.0], 95) == 10.0

    def test_p95_sorted(self):
        values = list(range(1, 101))  # 1..100
        p95 = _percentile([float(v) for v in values], 95)
        assert p95 >= 95.0
