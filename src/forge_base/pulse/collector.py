from typing import Any, Protocol, runtime_checkable

from forge_base.pulse.context import ExecutionContext


@runtime_checkable
class PulseCollector(Protocol):
    def on_start(self, context: ExecutionContext) -> None: ...
    def on_success(self, context: ExecutionContext, result: Any) -> None: ...
    def on_error(self, context: ExecutionContext, error: Exception) -> None: ...
    def on_finish(self, context: ExecutionContext) -> None: ...


class NoOpCollector:
    def on_start(self, context: ExecutionContext) -> None:
        pass

    def on_success(self, context: ExecutionContext, result: Any) -> None:
        pass

    def on_error(self, context: ExecutionContext, error: Exception) -> None:
        pass

    def on_finish(self, context: ExecutionContext) -> None:
        pass
