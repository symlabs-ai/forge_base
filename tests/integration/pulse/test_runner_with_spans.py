from typing import Any

import pytest

from forge_base.application.usecase_base import UseCaseBase
from forge_base.pulse.basic_collector import BasicCollector
from forge_base.pulse.budget import BudgetPolicy
from forge_base.pulse.context import _current_context
from forge_base.pulse.level import MonitoringLevel
from forge_base.pulse.policy import SamplingPolicy
from forge_base.pulse.runner import UseCaseRunner
from forge_base.pulse.span import pulse_span


class _StubMetrics:
    def __init__(self):
        self._counters: dict[str, int] = {}
        self._histograms: dict[str, list[float]] = {}

    def increment(self, name: str, value: int = 1, **tags: Any) -> None:
        self._counters[name] = self._counters.get(name, 0) + value

    def histogram(self, name: str, value: float, **tags: Any) -> None:
        self._histograms.setdefault(name, []).append(value)

    def gauge(self, name: str, value: float, **tags: Any) -> None:
        pass

    def report(self) -> dict[str, Any]:
        return {"counters": self._counters, "histograms": {}}


class _SpanningUseCase(UseCaseBase[str, str]):
    def _before_execute(self) -> None:
        pass

    def _after_execute(self) -> None:
        pass

    def _on_error(self, error: Exception) -> None:
        pass

    def execute(self, input_dto: str) -> str:
        with pulse_span("outer"):
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
class TestRunnerWithSpans:
    def setup_method(self):
        self._token = _current_context.set(None)

    def teardown_method(self):
        _current_context.reset(self._token)

    def test_spans_appear_in_record(self):
        metrics = _StubMetrics()
        collector = BasicCollector(metrics, level=MonitoringLevel.BASIC)
        uc = _SpanningUseCase()
        runner = UseCaseRunner(
            uc, level=MonitoringLevel.BASIC, collector=collector,
        )
        runner.run("hello")

        snap = collector.snapshot()
        assert len(snap.executions) == 1
        exec_dict = snap.executions[0]
        assert "spans" in exec_dict
        assert len(exec_dict["spans"]) == 2

    def test_nested_spans_parent_child_ids(self):
        metrics = _StubMetrics()
        collector = BasicCollector(metrics, level=MonitoringLevel.BASIC)
        uc = _SpanningUseCase()
        runner = UseCaseRunner(
            uc, level=MonitoringLevel.BASIC, collector=collector,
        )
        runner.run("hello")

        snap = collector.snapshot()
        spans = snap.executions[0]["spans"]
        # Spans in snapshot are simplified dicts with span_id, name, duration_ms, parent_span_id
        inner = next(s for s in spans if s["name"] == "inner")
        outer = next(s for s in spans if s["name"] == "outer")
        assert inner["parent_span_id"] == outer["span_id"]
        assert outer["parent_span_id"] == ""

    def test_budget_exceeded_drops_extra_spans(self):
        metrics = _StubMetrics()
        collector = BasicCollector(metrics, level=MonitoringLevel.BASIC)
        uc = _ManySpansUseCase(count=10)
        budget = BudgetPolicy(max_spans_per_execution=3)
        runner = UseCaseRunner(
            uc, level=MonitoringLevel.BASIC, collector=collector, budget=budget,
        )
        runner.run("hello")

        snap = collector.snapshot()
        exec_dict = snap.executions[0]
        assert "spans" in exec_dict
        assert len(exec_dict["spans"]) == 3

    def test_no_budget_unlimited_spans(self):
        metrics = _StubMetrics()
        collector = BasicCollector(metrics, level=MonitoringLevel.BASIC)
        uc = _ManySpansUseCase(count=100)
        runner = UseCaseRunner(
            uc, level=MonitoringLevel.BASIC, collector=collector, budget=None,
        )
        runner.run("hello")

        snap = collector.snapshot()
        exec_dict = snap.executions[0]
        assert len(exec_dict["spans"]) == 100

    def test_not_sampled_no_spans(self):
        metrics = _StubMetrics()
        collector = BasicCollector(metrics, level=MonitoringLevel.BASIC)
        uc = _SpanningUseCase()
        policy = SamplingPolicy(default_rate=0.0)
        runner = UseCaseRunner(
            uc, level=MonitoringLevel.BASIC, collector=collector, policy=policy,
        )
        runner.run("hello")

        snap = collector.snapshot()
        # Not sampled means no record at all
        assert len(snap.executions) == 0

    def test_pulse_span_outside_runner_noop(self):
        # pulse_span used without runner context is a silent no-op
        with pulse_span("orphan") as result:
            pass
        assert result is None
