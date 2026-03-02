from __future__ import annotations

from collections.abc import Generator
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, field
import time
from types import MappingProxyType
from typing import TYPE_CHECKING, Any
import uuid

if TYPE_CHECKING:
    from forge_base.pulse.budget import BudgetPolicy

_EMPTY_ATTRS: MappingProxyType[str, Any] = MappingProxyType({})


@dataclass(frozen=True)
class SpanRecord:
    span_id: str
    name: str
    start_ns: int
    end_ns: int
    duration_ms: float
    parent_span_id: str = ""
    attributes: MappingProxyType[str, Any] = field(default_factory=lambda: _EMPTY_ATTRS)


class _SpanAccumulator:
    __slots__ = ("_spans", "_budget", "_dropped")

    def __init__(self, budget: BudgetPolicy | None) -> None:
        self._spans: list[SpanRecord] = []
        self._budget = budget
        self._dropped: int = 0

    def can_add_span(self) -> bool:
        # Soft budget: checked at span entry, added at span exit. Nested spans
        # admitted before children finish may push total slightly over the limit.
        if self._budget is None:
            return True
        return len(self._spans) < self._budget.max_spans_per_execution

    def add(self, span: SpanRecord) -> None:
        self._spans.append(span)

    def drop(self) -> None:
        self._dropped += 1

    def harvest(self) -> list[SpanRecord]:
        return list(self._spans)

    @property
    def dropped_count(self) -> int:
        return self._dropped


_span_accumulator: ContextVar[_SpanAccumulator | None] = ContextVar(
    "pulse_span_accumulator", default=None
)
_current_span_id: ContextVar[str] = ContextVar(
    "pulse_current_span_id", default=""
)


@contextmanager
def pulse_span(
    name: str, **attributes: Any
) -> Generator[SpanRecord | None, None, None]:
    acc = _span_accumulator.get()
    if acc is None:
        yield None
        return
    if not acc.can_add_span():
        acc.drop()
        yield None
        return

    parent_id = _current_span_id.get()
    span_id = str(uuid.uuid4())
    token = _current_span_id.set(span_id)
    start_ns = time.perf_counter_ns()
    try:
        yield None  # SpanRecord is frozen; created in finally with measured duration
    finally:
        end_ns = time.perf_counter_ns()
        duration_ms = (end_ns - start_ns) / 1_000_000
        attrs = MappingProxyType(attributes) if attributes else _EMPTY_ATTRS
        span = SpanRecord(
            span_id=span_id,
            name=name,
            start_ns=start_ns,
            end_ns=end_ns,
            duration_ms=duration_ms,
            parent_span_id=parent_id,
            attributes=attrs,
        )
        acc.add(span)
        _current_span_id.reset(token)
