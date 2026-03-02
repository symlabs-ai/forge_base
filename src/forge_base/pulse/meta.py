from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import TypeVar

_C = TypeVar("_C", bound=type)

_PULSE_META_ATTR = "__pulse_meta__"
_EMPTY_TAGS: MappingProxyType[str, str] = MappingProxyType({})


@dataclass(frozen=True)
class PulseMeta:
    subtrack: str = ""
    feature: str = ""
    value_track: str = ""
    tags: MappingProxyType[str, str] = field(default_factory=lambda: _EMPTY_TAGS)


def pulse_meta(
    subtrack: str = "",
    feature: str = "",
    value_track: str = "",
    tags: dict[str, str] | None = None,
) -> Callable[[_C], _C]:
    """Class decorator -- metadata only, no execution wrapping."""

    def decorator(cls: type) -> type:
        cls.__pulse_meta__ = PulseMeta(  # type: ignore[attr-defined]
            subtrack=subtrack,
            feature=feature,
            value_track=value_track,
            tags=MappingProxyType(tags or {}),
        )
        return cls

    return decorator


def read_pulse_meta(use_case: object) -> PulseMeta | None:
    return getattr(type(use_case), _PULSE_META_ATTR, None)
