from dataclasses import dataclass, field
from pathlib import Path
from types import MappingProxyType

import yaml

from forge_base.pulse.exceptions import PulseConfigError
from forge_base.pulse.spec_schema import validate_spec

_EMPTY_TAGS: MappingProxyType[str, str] = MappingProxyType({})


@dataclass(frozen=True)
class ValueTrackMapping:
    value_track: str
    subtrack: str = ""
    tags: MappingProxyType[str, str] = field(default_factory=lambda: _EMPTY_TAGS)
    mapping_source: str = "spec"


class ValueTrackRegistry:
    __slots__ = ("_index",)

    def __init__(self) -> None:
        self._index: dict[str, ValueTrackMapping] = {}

    def load_from_yaml(self, path: str | Path) -> None:
        p = Path(path)
        if not p.exists():
            raise PulseConfigError(f"spec file not found: {p}")

        try:
            with open(p, encoding="utf-8") as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as exc:
            raise PulseConfigError(f"invalid YAML in {p}: {exc}") from exc

        if data is None:
            raise PulseConfigError(f"spec file is empty: {p}")

        self.load_from_dict(data)

    def load_from_dict(self, data: dict) -> None:
        validate_spec(data)

        tracks = data["value_tracks"]
        for track_name, track_def in tracks.items():
            usecases = track_def["usecases"]
            tags_raw = track_def.get("tags", {})
            tags = MappingProxyType(tags_raw) if tags_raw else _EMPTY_TAGS

            # Build subtrack index: usecase → subtrack_name
            subtrack_index: dict[str, str] = {}
            for sub_name, sub_usecases in track_def.get("subtracks", {}).items():
                for uc in sub_usecases:
                    subtrack_index[uc] = sub_name

            for uc in usecases:
                if uc in self._index:
                    existing = self._index[uc]
                    raise PulseConfigError(
                        f"usecase '{uc}' already mapped to track "
                        f"'{existing.value_track}', cannot remap to '{track_name}'"
                    )
                self._index[uc] = ValueTrackMapping(
                    value_track=track_name,
                    subtrack=subtrack_index.get(uc, ""),
                    tags=tags,
                )

    def resolve(self, use_case_name: str) -> ValueTrackMapping | None:
        return self._index.get(use_case_name)
