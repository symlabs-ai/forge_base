import time

import pytest

from forge_base.application.usecase_base import UseCaseBase
from forge_base.pulse.level import MonitoringLevel
from forge_base.pulse.runner import UseCaseRunner


class _NoOpUseCase(UseCaseBase[str, str]):
    def _before_execute(self) -> None:
        pass

    def _after_execute(self) -> None:
        pass

    def _on_error(self, error: Exception) -> None:
        pass

    def execute(self, input_dto: str) -> str:
        return input_dto


ITERATIONS = 100_000


@pytest.mark.pulse_benchmark
class TestPulseOverhead:
    def test_off_overhead_under_100ns(self):
        uc = _NoOpUseCase()
        runner = UseCaseRunner(uc, level=MonitoringLevel.OFF)

        # warmup
        for _ in range(1000):
            runner.run("x")

        # direct execute baseline
        start = time.perf_counter_ns()
        for _ in range(ITERATIONS):
            uc.execute("x")
        direct_ns = time.perf_counter_ns() - start

        # runner.run(OFF) path
        start = time.perf_counter_ns()
        for _ in range(ITERATIONS):
            runner.run("x")
        runner_ns = time.perf_counter_ns() - start

        overhead_per_call = (runner_ns - direct_ns) / ITERATIONS
        print(f"\nDirect: {direct_ns / ITERATIONS:.1f} ns/call")
        print(f"Runner(OFF): {runner_ns / ITERATIONS:.1f} ns/call")
        print(f"Overhead: {overhead_per_call:.1f} ns/call")

        assert overhead_per_call < 100, (
            f"Overhead {overhead_per_call:.1f}ns exceeds 100ns budget"
        )
