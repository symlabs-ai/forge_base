from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from forge_base.pulse.report import PulseSnapshot


@dataclass(frozen=True)
class TrackSummary:
    value_track: str
    total_executions: int
    successful: int
    failed: int
    error_rate: float
    mean_duration_ms: float
    p95_duration_ms: float


@dataclass(frozen=True)
class DashboardSummary:
    total_executions: int
    successful: int
    failed: int
    error_rate: float
    mean_duration_ms: float
    top_error_types: tuple[tuple[str, int], ...]
    by_value_track: tuple[TrackSummary, ...]

    @classmethod
    def from_snapshot(cls, snapshot: PulseSnapshot, top_n: int = 5) -> DashboardSummary:
        execs = snapshot.executions
        total = len(execs)

        if total == 0:
            return cls(
                total_executions=0,
                successful=0,
                failed=0,
                error_rate=0.0,
                mean_duration_ms=0.0,
                top_error_types=(),
                by_value_track=(),
            )

        successful = sum(1 for e in execs if e.get("success", False))
        failed = total - successful
        error_rate = failed / total

        durations = [e["duration_ms"] for e in execs]
        mean_duration = sum(durations) / total

        error_counts: Counter[str] = Counter()
        for e in execs:
            et = e.get("error_type", "")
            if et:
                error_counts[et] += 1
        top_errors = tuple(error_counts.most_common(top_n))

        tracks: dict[str, list[dict]] = {}
        for e in execs:
            vt = e.get("value_track", "legacy")
            tracks.setdefault(vt, []).append(e)

        track_summaries = []
        for vt_name in sorted(tracks):
            track_execs = tracks[vt_name]
            t_total = len(track_execs)
            t_success = sum(1 for e in track_execs if e.get("success", False))
            t_failed = t_total - t_success
            t_durations = [e["duration_ms"] for e in track_execs]
            track_summaries.append(
                TrackSummary(
                    value_track=vt_name,
                    total_executions=t_total,
                    successful=t_success,
                    failed=t_failed,
                    error_rate=t_failed / t_total,
                    mean_duration_ms=sum(t_durations) / t_total,
                    p95_duration_ms=_percentile(t_durations, 95),
                )
            )

        return cls(
            total_executions=total,
            successful=successful,
            failed=failed,
            error_rate=error_rate,
            mean_duration_ms=mean_duration,
            top_error_types=top_errors,
            by_value_track=tuple(track_summaries),
        )


def _percentile(values: list[float], pct: int) -> float:
    if not values:
        return 0.0
    sorted_vals = sorted(values)
    idx = min(int(len(sorted_vals) * pct / 100), len(sorted_vals) - 1)
    return sorted_vals[idx]
