from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    from forge_base.pulse.context import ExecutionContext


@runtime_checkable
class PulseMetricsProtocol(Protocol):
    def increment(self, name: str, value: int = 1, **tags: Any) -> None: ...
    def histogram(self, name: str, value: float, **tags: Any) -> None: ...
    def gauge(self, name: str, value: float, **tags: Any) -> None: ...


@runtime_checkable
class PulseExporterProtocol(Protocol):
    def export(self, context: ExecutionContext, data: dict[str, Any]) -> None: ...
