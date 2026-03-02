from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from forge_base.application.usecase_base import UseCaseBase

_INFRA_SEGMENTS = frozenset({
    "usecases",
    "use_cases",
    "application",
    "services",
    "handlers",
    "commands",
    "queries",
})


def infer_context(use_case: UseCaseBase) -> dict[str, str]:  # type: ignore[type-arg]
    cls = type(use_case)
    module = cls.__module__ or ""
    name = cls.__name__

    return {
        "use_case_name": name,
        "feature": _extract_feature(module),
        "value_track": "legacy",
        "subtrack": _extract_domain(module),
        "mapping_source": "heuristic",
    }


def _extract_feature(module: str) -> str:
    if not module:
        return ""
    parts = module.rsplit(".", 1)
    return parts[-1] if parts else ""


def _extract_domain(module: str) -> str:
    if not module:
        return ""
    parts = module.split(".")
    # Skip last segment (feature, already handled by _extract_feature)
    for segment in reversed(parts[:-1]):
        if segment not in _INFRA_SEGMENTS:
            return segment
    return parts[0] if parts else ""
