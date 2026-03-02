from types import MappingProxyType

import pytest

from forge_base.pulse.budget import BudgetPolicy
from forge_base.pulse.span import (  # noqa: I001
    SpanRecord,
    _current_span_id,
    _span_accumulator,
    _SpanAccumulator,
    pulse_span,
)


@pytest.mark.pulse
class TestSpanRecord:
    def test_frozen(self):
        span = SpanRecord(
            span_id="a", name="op", start_ns=0, end_ns=1000, duration_ms=0.001
        )
        with pytest.raises(AttributeError):
            span.name = "changed"  # type: ignore[misc]

    def test_defaults(self):
        span = SpanRecord(
            span_id="a", name="op", start_ns=0, end_ns=1000, duration_ms=0.001
        )
        assert span.parent_span_id == ""
        assert span.attributes == MappingProxyType({})

    def test_attributes_is_mapping_proxy(self):
        attrs = MappingProxyType({"key": "val"})
        span = SpanRecord(
            span_id="a", name="op", start_ns=0, end_ns=1000, duration_ms=0.001,
            attributes=attrs,
        )
        assert isinstance(span.attributes, MappingProxyType)
        assert span.attributes["key"] == "val"


@pytest.mark.pulse
class TestPulseSpan:
    def setup_method(self):
        self._acc_token = _span_accumulator.set(None)
        self._span_token = _current_span_id.set("")

    def teardown_method(self):
        _span_accumulator.reset(self._acc_token)
        _current_span_id.reset(self._span_token)

    def test_basic_span(self):
        acc = _SpanAccumulator(budget=None)
        token = _span_accumulator.set(acc)
        try:
            with pulse_span("my_op"):
                pass
            spans = acc.harvest()
            assert len(spans) == 1
            assert spans[0].name == "my_op"
            assert spans[0].duration_ms > 0
            assert spans[0].parent_span_id == ""
        finally:
            _span_accumulator.reset(token)

    def test_nested_parent_child(self):
        acc = _SpanAccumulator(budget=None)
        token = _span_accumulator.set(acc)
        try:
            with pulse_span("parent"):
                with pulse_span("child"):
                    pass
            spans = acc.harvest()
            assert len(spans) == 2
            child, parent = spans[0], spans[1]
            assert child.name == "child"
            assert parent.name == "parent"
            assert child.parent_span_id == parent.span_id
            assert parent.parent_span_id == ""
        finally:
            _span_accumulator.reset(token)

    def test_no_accumulator_is_noop(self):
        # _span_accumulator is None by default (from setup_method)
        with pulse_span("ignored") as result:
            pass
        assert result is None

    def test_duration_positive(self):
        acc = _SpanAccumulator(budget=None)
        token = _span_accumulator.set(acc)
        try:
            with pulse_span("timed"):
                for _ in range(100):
                    pass
            spans = acc.harvest()
            assert spans[0].duration_ms >= 0
            assert spans[0].end_ns > spans[0].start_ns
        finally:
            _span_accumulator.reset(token)

    def test_attributes_forwarded(self):
        acc = _SpanAccumulator(budget=None)
        token = _span_accumulator.set(acc)
        try:
            with pulse_span("db_query", table="users", limit=10):
                pass
            spans = acc.harvest()
            assert spans[0].attributes["table"] == "users"
            assert spans[0].attributes["limit"] == 10
        finally:
            _span_accumulator.reset(token)


@pytest.mark.pulse
class TestSpanAccumulator:
    def test_harvest_returns_list(self):
        acc = _SpanAccumulator(budget=None)
        span = SpanRecord(
            span_id="a", name="op", start_ns=0, end_ns=1000, duration_ms=0.001
        )
        acc.add(span)
        harvested = acc.harvest()
        assert len(harvested) == 1
        assert harvested[0] is span
        # harvest returns a copy
        assert harvested is not acc.harvest()

    def test_budget_enforced(self):
        budget = BudgetPolicy(max_spans_per_execution=2)
        acc = _SpanAccumulator(budget=budget)
        for i in range(3):
            if acc.can_add_span():
                acc.add(SpanRecord(
                    span_id=str(i), name=f"op{i}", start_ns=0, end_ns=1, duration_ms=0.0
                ))
            else:
                acc.drop()
        assert len(acc.harvest()) == 2
        assert acc.dropped_count == 1

    def test_dropped_count(self):
        budget = BudgetPolicy(max_spans_per_execution=1)
        acc = _SpanAccumulator(budget=budget)
        acc.add(SpanRecord(span_id="a", name="op", start_ns=0, end_ns=1, duration_ms=0.0))
        assert not acc.can_add_span()
        acc.drop()
        acc.drop()
        assert acc.dropped_count == 2

    def test_unlimited_when_no_budget(self):
        acc = _SpanAccumulator(budget=None)
        for i in range(200):
            assert acc.can_add_span()
            acc.add(SpanRecord(
                span_id=str(i), name=f"op{i}", start_ns=0, end_ns=1, duration_ms=0.0
            ))
        assert len(acc.harvest()) == 200


@pytest.mark.pulse
class TestBudgetEnforcement:
    def setup_method(self):
        self._acc_token = _span_accumulator.set(None)
        self._span_token = _current_span_id.set("")

    def teardown_method(self):
        _span_accumulator.reset(self._acc_token)
        _current_span_id.reset(self._span_token)

    def test_max_spans_reached_noop(self):
        budget = BudgetPolicy(max_spans_per_execution=2)
        acc = _SpanAccumulator(budget=budget)
        token = _span_accumulator.set(acc)
        try:
            for _ in range(5):
                with pulse_span("op"):
                    pass
            spans = acc.harvest()
            assert len(spans) == 2
            assert acc.dropped_count == 3
        finally:
            _span_accumulator.reset(token)

    def test_spans_within_limit(self):
        budget = BudgetPolicy(max_spans_per_execution=10)
        acc = _SpanAccumulator(budget=budget)
        token = _span_accumulator.set(acc)
        try:
            for _ in range(5):
                with pulse_span("op"):
                    pass
            spans = acc.harvest()
            assert len(spans) == 5
            assert acc.dropped_count == 0
        finally:
            _span_accumulator.reset(token)

    def test_nested_spans_count_towards_budget(self):
        # Budget=2: parent admitted at entry (0<2), child1 (0<2), child2 (1<2),
        # child3 rejected (2<2=False). Parent added at exit → total 3 spans, 1 dropped.
        budget = BudgetPolicy(max_spans_per_execution=2)
        acc = _SpanAccumulator(budget=budget)
        token = _span_accumulator.set(acc)
        try:
            with pulse_span("parent"):
                with pulse_span("child1"):
                    pass
                with pulse_span("child2"):
                    pass
                with pulse_span("child3_dropped"):
                    pass
            spans = acc.harvest()
            assert len(spans) == 3
            assert acc.dropped_count == 1
        finally:
            _span_accumulator.reset(token)
