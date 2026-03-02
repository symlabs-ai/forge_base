from __future__ import annotations

from dataclasses import dataclass

from forge_base.pulse.exceptions import PulseConfigError


def _validate_positive_int(value: object, label: str) -> None:
    if not isinstance(value, int) or isinstance(value, bool):
        raise PulseConfigError(f"{label} must be an int, got {type(value).__name__}")
    if value < 1:
        raise PulseConfigError(f"{label} must be >= 1, got {value}")


@dataclass(frozen=True)
class BudgetPolicy:
    max_spans_per_execution: int = 64
    max_events_per_execution: int = 128

    def __post_init__(self) -> None:
        _validate_positive_int(self.max_spans_per_execution, "max_spans_per_execution")
        _validate_positive_int(self.max_events_per_execution, "max_events_per_execution")
