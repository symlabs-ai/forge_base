import time
from types import MappingProxyType

import pytest

from forge_base.pulse.context import ExecutionContext
from forge_base.pulse.level import MonitoringLevel
from forge_base.pulse.policy import SamplingPolicy

ITERATIONS = 100_000


@pytest.mark.pulse_benchmark
class TestPolicyOverhead:
    def test_should_sample_under_1us(self):
        policy = SamplingPolicy(
            default_rate=0.5,
            by_value_track={"revenue": 0.8, "growth": 0.3, "ops": 0.1},
            by_tenant={"acme": 0.9, "beta": 0.2},
        )
        ctx = ExecutionContext(
            correlation_id="bench",
            level=MonitoringLevel.BASIC,
            use_case_name="BenchUC",
            value_track="revenue",
            extra=MappingProxyType({"tenant": "acme"}),
        )

        # warmup
        for _ in range(1000):
            policy.should_sample(ctx)

        start = time.perf_counter_ns()
        for _ in range(ITERATIONS):
            policy.should_sample(ctx)
        elapsed_ns = time.perf_counter_ns() - start

        per_call_us = elapsed_ns / ITERATIONS / 1000
        print(f"\nshould_sample per-call: {per_call_us:.3f} us")

        assert per_call_us < 1.0, (
            f"should_sample overhead {per_call_us:.3f}us exceeds 1us budget"
        )
