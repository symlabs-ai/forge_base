from typing import Any, Generic, TypeVar

from forge_base.application.usecase_base import UseCaseBase
from forge_base.pulse.collector import NoOpCollector, PulseCollector
from forge_base.pulse.context import ExecutionContext, _current_context, set_context
from forge_base.pulse.level import MonitoringLevel

TInput = TypeVar("TInput")
TOutput = TypeVar("TOutput")


class UseCaseRunner(Generic[TInput, TOutput]):
    __slots__ = ("_use_case", "_level", "_off", "_collector", "_execute")

    def __init__(
        self,
        use_case: UseCaseBase[TInput, TOutput],
        level: MonitoringLevel = MonitoringLevel.OFF,
        collector: PulseCollector | None = None,
    ) -> None:
        self._use_case = use_case
        self._level = level
        self._off: bool = level == MonitoringLevel.OFF
        self._collector: PulseCollector = collector or NoOpCollector()
        # Bound method ref avoids attribute lookup on hot path (~30ns saving)
        self._execute = use_case.execute

    def run(self, input_dto: TInput, **ctx_overrides: Any) -> TOutput:
        if self._off:
            return self._execute(input_dto)

        ctx = ExecutionContext.build(
            level=self._level,
            use_case_name=type(self._use_case).__name__,
            **ctx_overrides,
        )
        token = set_context(ctx)
        try:
            self._collector.on_start(ctx)
            result = self._use_case.execute(input_dto)
            self._collector.on_success(ctx, result)
            return result
        except Exception as exc:
            self._collector.on_error(ctx, exc)
            raise
        finally:
            self._collector.on_finish(ctx)
            _current_context.reset(token)
