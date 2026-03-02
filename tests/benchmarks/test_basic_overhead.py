import time

import pytest

from forge_base.application.usecase_base import UseCaseBase
from forge_base.pulse.basic_collector import BasicCollector
from forge_base.pulse.level import MonitoringLevel
from forge_base.pulse.runner import UseCaseRunner
from forge_base.testing.fakes.fake_metrics_collector import FakeMetricsCollector


class _NoOpUseCase(UseCaseBase[str, str]):
    def _before_execute(self) -> None:
        pass

    def _after_execute(self) -> None:
        pass

    def _on_error(self, error: Exception) -> None:
        pass

    def execute(self, input_dto: str) -> str:
        return input_dto


ITERATIONS = 10_000


@pytest.mark.pulse_benchmark
class TestBasicCollectorOverhead:
    def test_basic_under_10us(self):
        metrics = FakeMetricsCollector()
        collector = BasicCollector(metrics, level=MonitoringLevel.BASIC)
        uc = _NoOpUseCase()
        runner = UseCaseRunner(uc, level=MonitoringLevel.BASIC, collector=collector)

        # warmup
        for _ in range(500):
            runner.run("x")

        start = time.perf_counter_ns()
        for _ in range(ITERATIONS):
            runner.run("x")
        elapsed_ns = time.perf_counter_ns() - start

        per_call_us = elapsed_ns / ITERATIONS / 1000
        print(f"\nBASIC per-call: {per_call_us:.2f} us")

        assert per_call_us < 10, (
            f"BASIC overhead {per_call_us:.2f}us exceeds 10us budget"
        )
