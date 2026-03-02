from __future__ import annotations

from dataclasses import dataclass, field
import random
from types import MappingProxyType
from typing import TYPE_CHECKING

from forge_base.pulse.exceptions import PulseConfigError

if TYPE_CHECKING:
    from forge_base.pulse.context import ExecutionContext

_EMPTY_RATES: MappingProxyType[str, float] = MappingProxyType({})


def _validate_rate(value: float, label: str) -> None:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise PulseConfigError(f"{label} must be a float, got {type(value).__name__}")
    if value < 0.0 or value > 1.0:
        raise PulseConfigError(f"{label} must be between 0.0 and 1.0, got {value}")


@dataclass(frozen=True)
class SamplingPolicy:
    """Probabilistic sampling policy for pulse instrumentation.

    Resolution order (most specific wins):
        1. by_tenant — keyed on ctx.extra["tenant"]
        2. by_value_track — keyed on ctx.value_track
        3. default_rate — fallback
    """

    default_rate: float = 1.0
    by_value_track: MappingProxyType[str, float] = field(default_factory=lambda: _EMPTY_RATES)
    by_tenant: MappingProxyType[str, float] = field(default_factory=lambda: _EMPTY_RATES)

    def __post_init__(self) -> None:
        _validate_rate(self.default_rate, "default_rate")
        # Freeze mutable dicts passed by callers (copy to detach from original)
        if isinstance(self.by_value_track, dict):
            object.__setattr__(self, "by_value_track", MappingProxyType(dict(self.by_value_track)))
        if isinstance(self.by_tenant, dict):
            object.__setattr__(self, "by_tenant", MappingProxyType(dict(self.by_tenant)))
        for key, rate in self.by_value_track.items():
            _validate_rate(rate, f"by_value_track[{key!r}]")
        for key, rate in self.by_tenant.items():
            _validate_rate(rate, f"by_tenant[{key!r}]")

    def should_sample(self, ctx: ExecutionContext) -> bool:
        """Decide whether this execution should be instrumented."""
        tenant = ctx.extra.get("tenant", "")
        if tenant and tenant in self.by_tenant:
            rate = self.by_tenant[tenant]
        elif ctx.value_track in self.by_value_track:
            rate = self.by_value_track[ctx.value_track]
        else:
            rate = self.default_rate
        return random.random() < rate  # noqa: S311
