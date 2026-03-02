from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generic, TypeVar

from forge_base.application.usecase_base import UseCaseBase
from forge_base.pulse.collector import NoOpCollector, PulseCollector
from forge_base.pulse.context import ExecutionContext, _current_context, set_context
from forge_base.pulse.heuristic import infer_context
from forge_base.pulse.level import MonitoringLevel
from forge_base.pulse.meta import read_pulse_meta

if TYPE_CHECKING:
    from forge_base.pulse.budget import BudgetPolicy
    from forge_base.pulse.policy import SamplingPolicy
    from forge_base.pulse.value_tracks import ValueTrackRegistry

TInput = TypeVar("TInput")
TOutput = TypeVar("TOutput")


class UseCaseRunner(Generic[TInput, TOutput]):
    __slots__ = (
        "_use_case", "_level", "_off", "_collector", "_execute", "_inferred", "_registry",
        "_policy", "_budget",
    )

    def __init__(
        self,
        use_case: UseCaseBase[TInput, TOutput],
        level: MonitoringLevel = MonitoringLevel.OFF,
        collector: PulseCollector | None = None,
        registry: ValueTrackRegistry | None = None,
        policy: SamplingPolicy | None = None,
        budget: BudgetPolicy | None = None,
    ) -> None:
        self._use_case = use_case
        self._level = level
        self._off: bool = level == MonitoringLevel.OFF
        self._collector: PulseCollector = collector or NoOpCollector()
        self._registry = registry
        self._policy = policy
        self._budget = budget
        # Bound method ref avoids attribute lookup on hot path (~30ns saving)
        self._execute = use_case.execute
        self._inferred: dict[str, str] = infer_context(use_case) if not self._off else {}
        if not self._off:
            meta = read_pulse_meta(use_case)
            if meta is not None:
                _any_overridden = False
                if meta.subtrack:
                    self._inferred["subtrack"] = meta.subtrack
                    _any_overridden = True
                if meta.feature:
                    self._inferred["feature"] = meta.feature
                    _any_overridden = True
                if meta.value_track:
                    self._inferred["value_track"] = meta.value_track
                    _any_overridden = True
                if _any_overridden:
                    self._inferred["mapping_source"] = "decorator"

    def run(self, input_dto: TInput, **ctx_overrides: Any) -> TOutput:
        if self._off:
            return self._execute(input_dto)

        resolved = dict(self._inferred)
        if self._registry is not None:
            mapping = self._registry.resolve(resolved.get("use_case_name", ""))
            if mapping is not None:
                resolved["value_track"] = mapping.value_track
                resolved["subtrack"] = mapping.subtrack or resolved.get("subtrack", "")
                resolved["mapping_source"] = mapping.mapping_source
        resolved.update(ctx_overrides)

        ctx = ExecutionContext.build(
            level=self._level,
            **resolved,
        )
        token = set_context(ctx)
        sampled = self._policy is None or self._policy.should_sample(ctx)

        acc_token = None
        span_token = None
        if sampled:
            from forge_base.pulse.span import _current_span_id, _span_accumulator, _SpanAccumulator

            acc = _SpanAccumulator(self._budget)
            acc_token = _span_accumulator.set(acc)
            span_token = _current_span_id.set("")

        try:
            if sampled:
                self._collector.on_start(ctx)
            result = self._use_case.execute(input_dto)
            if sampled:
                self._collector.on_success(ctx, result)
            return result
        except Exception as exc:
            if sampled:
                self._collector.on_error(ctx, exc)
            raise
        finally:
            # on_finish must run before resetting the accumulator — BasicCollector
            # harvests spans from _span_accumulator inside on_finish.
            if sampled:
                self._collector.on_finish(ctx)
            if sampled and acc_token is not None and span_token is not None:
                _span_accumulator.reset(acc_token)
                _current_span_id.reset(span_token)
            _current_context.reset(token)
