from forge_base.pulse.exceptions import PulseConfigError

SUPPORTED_SPEC_VERSIONS: frozenset[str] = frozenset({"0.1"})


def validate_spec(data: dict) -> None:  # noqa: C901
    if not isinstance(data, dict):
        raise PulseConfigError(f"spec must be a dict, got {type(data).__name__}")

    # --- schema_version ---
    if "schema_version" not in data:
        raise PulseConfigError("spec missing required key 'schema_version'")

    version = data["schema_version"]
    if not isinstance(version, str):
        raise PulseConfigError(
            f"'schema_version' must be a string, got {type(version).__name__}"
        )
    if version not in SUPPORTED_SPEC_VERSIONS:
        raise PulseConfigError(
            f"unsupported schema_version '{version}', "
            f"supported: {sorted(SUPPORTED_SPEC_VERSIONS)}"
        )

    # --- value_tracks ---
    if "value_tracks" not in data:
        raise PulseConfigError("spec missing required key 'value_tracks'")

    tracks = data["value_tracks"]
    if not isinstance(tracks, dict):
        raise PulseConfigError(
            f"'value_tracks' must be a dict, got {type(tracks).__name__}"
        )
    if not tracks:
        raise PulseConfigError("'value_tracks' must not be empty")

    for track_name, track_def in tracks.items():
        _validate_track(track_name, track_def)


def _validate_track(track_name: str, track_def: dict) -> None:
    if not isinstance(track_def, dict):
        raise PulseConfigError(
            f"track '{track_name}' must be a dict, got {type(track_def).__name__}"
        )

    # --- usecases (required) ---
    if "usecases" not in track_def:
        raise PulseConfigError(f"track '{track_name}' missing required key 'usecases'")

    usecases = track_def["usecases"]
    if not isinstance(usecases, list):
        raise PulseConfigError(
            f"track '{track_name}' 'usecases' must be a list, "
            f"got {type(usecases).__name__}"
        )
    if not usecases:
        raise PulseConfigError(f"track '{track_name}' 'usecases' must not be empty")

    for i, uc in enumerate(usecases):
        if not isinstance(uc, str):
            raise PulseConfigError(
                f"track '{track_name}' usecases[{i}] must be a string, "
                f"got {type(uc).__name__}"
            )

    usecase_set = set(usecases)
    if len(usecase_set) != len(usecases):
        seen: set[str] = set()
        for uc in usecases:
            if uc in seen:
                raise PulseConfigError(
                    f"track '{track_name}' has duplicate usecase '{uc}'"
                )
            seen.add(uc)

    # --- subtracks (optional) ---
    if "subtracks" in track_def:
        subtracks = track_def["subtracks"]
        if not isinstance(subtracks, dict):
            raise PulseConfigError(
                f"track '{track_name}' 'subtracks' must be a dict, "
                f"got {type(subtracks).__name__}"
            )
        for sub_name, sub_usecases in subtracks.items():
            if not isinstance(sub_usecases, list):
                raise PulseConfigError(
                    f"track '{track_name}' subtrack '{sub_name}' must be a list, "
                    f"got {type(sub_usecases).__name__}"
                )
            for j, suc in enumerate(sub_usecases):
                if not isinstance(suc, str):
                    raise PulseConfigError(
                        f"track '{track_name}' subtrack '{sub_name}'[{j}] "
                        f"must be a string, got {type(suc).__name__}"
                    )
                if suc not in usecase_set:
                    raise PulseConfigError(
                        f"track '{track_name}' subtrack '{sub_name}' references "
                        f"unknown usecase '{suc}' (not in usecases list)"
                    )

    # --- tags (optional) ---
    if "tags" in track_def:
        tags = track_def["tags"]
        if not isinstance(tags, dict):
            raise PulseConfigError(
                f"track '{track_name}' 'tags' must be a dict, "
                f"got {type(tags).__name__}"
            )
        for k, v in tags.items():
            if not isinstance(v, str):
                raise PulseConfigError(
                    f"track '{track_name}' tag '{k}' value must be a string, "
                    f"got {type(v).__name__}"
                )

    # --- description (optional) ---
    if "description" in track_def:
        desc = track_def["description"]
        if not isinstance(desc, str):
            raise PulseConfigError(
                f"track '{track_name}' 'description' must be a string, "
                f"got {type(desc).__name__}"
            )
