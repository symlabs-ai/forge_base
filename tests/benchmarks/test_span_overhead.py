import time

import pytest

from forge_base.pulse.budget import BudgetPolicy
from forge_base.pulse.span import (
    _current_span_id,
    _span_accumulator,
    _SpanAccumulator,
    pulse_span,
)

ITERATIONS = 100_000


@pytest.mark.pulse_benchmark
class TestSpanOverhead:
    def test_pulse_span_under_5us(self):
        budget = BudgetPolicy(max_spans_per_execution=ITERATIONS + 1000)
        acc = _SpanAccumulator(budget=budget)
        acc_token = _span_accumulator.set(acc)
        span_token = _current_span_id.set("")
        try:
            # warmup
            for _ in range(1000):
                with pulse_span("warmup"):
                    pass

            # reset accumulator for clean measurement
            acc2 = _SpanAccumulator(budget=BudgetPolicy(max_spans_per_execution=ITERATIONS + 1))
            acc_token2 = _span_accumulator.set(acc2)

            start = time.perf_counter_ns()
            for _ in range(ITERATIONS):
                with pulse_span("bench"):
                    pass
            elapsed_ns = time.perf_counter_ns() - start

            per_call_us = (elapsed_ns / ITERATIONS) / 1_000
            print(f"\npulse_span: {per_call_us:.2f} us/call")

            _span_accumulator.reset(acc_token2)

            assert per_call_us < 5, (
                f"pulse_span overhead {per_call_us:.2f}us exceeds 5us budget"
            )
        finally:
            _span_accumulator.reset(acc_token)
            _current_span_id.reset(span_token)
