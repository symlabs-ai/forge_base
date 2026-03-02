from contextvars import ContextVar, Token
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any
import uuid

from forge_base.pulse.level import MonitoringLevel
from forge_base.pulse.redaction import redact_keys


@dataclass(frozen=True)
class ExecutionContext:
    correlation_id: str
    level: MonitoringLevel = MonitoringLevel.OFF
    use_case_name: str = ""
    value_track: str = "legacy"
    subtrack: str = ""
    feature: str = ""
    mapping_source: str = "legacy"
    extra: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))

    @classmethod
    def build(
        cls,
        correlation_id: str | None = None,
        *,
        extra: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> "ExecutionContext":
        cid = correlation_id or str(uuid.uuid4())
        safe_extra = redact_keys(extra) if extra else {}
        return cls(correlation_id=cid, extra=MappingProxyType(safe_extra), **kwargs)


_current_context: ContextVar[ExecutionContext | None] = ContextVar(
    "pulse_context", default=None
)


def get_context() -> ExecutionContext | None:
    return _current_context.get()


def set_context(ctx: ExecutionContext) -> Token[ExecutionContext | None]:
    return _current_context.set(ctx)
