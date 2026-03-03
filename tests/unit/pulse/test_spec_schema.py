import pytest

from forge_base.pulse.exceptions import PulseConfigError
from forge_base.pulse.spec_schema import SUPPORTED_SPEC_VERSIONS, validate_spec


def _minimal_spec(**overrides):
    base = {
        "schema_version": "0.1",
        "value_tracks": {
            "core": {
                "usecases": ["CreateOrder"],
            },
        },
    }
    base.update(overrides)
    return base


@pytest.mark.pulse
class TestValidateSpecValid:
    def test_minimal_spec_passes(self):
        validate_spec(_minimal_spec())

    def test_spec_with_subtracks(self):
        spec = _minimal_spec()
        spec["value_tracks"]["core"]["subtracks"] = {"checkout": ["CreateOrder"]}
        validate_spec(spec)

    def test_spec_with_tags(self):
        spec = _minimal_spec()
        spec["value_tracks"]["core"]["tags"] = {"tier": "premium"}
        validate_spec(spec)

    def test_spec_with_description(self):
        spec = _minimal_spec()
        spec["value_tracks"]["core"]["description"] = "Core business track"
        validate_spec(spec)

    def test_spec_with_multiple_tracks(self):
        spec = _minimal_spec()
        spec["value_tracks"]["support"] = {"usecases": ["TicketReply"]}
        validate_spec(spec)

    def test_supported_versions_is_frozenset(self):
        assert isinstance(SUPPORTED_SPEC_VERSIONS, frozenset)
        assert "0.1" in SUPPORTED_SPEC_VERSIONS
        assert "0.2" in SUPPORTED_SPEC_VERSIONS

    def test_v02_minimal_spec(self):
        validate_spec({
            "schema_version": "0.2",
            "value_tracks": {"core": {"usecases": ["CreateOrder"]}},
        })

    def test_v02_with_support_tracks(self):
        validate_spec({
            "schema_version": "0.2",
            "value_tracks": {"ProcessOrder": {"usecases": ["CreateOrder"]}},
            "support_tracks": {
                "ManageInventory": {
                    "supports": ["ProcessOrder"],
                    "usecases": ["SyncInventory"],
                },
            },
        })

    def test_v02_support_tracks_with_tags_and_description(self):
        validate_spec({
            "schema_version": "0.2",
            "value_tracks": {"ProcessOrder": {"usecases": ["CreateOrder"]}},
            "support_tracks": {
                "ManageInventory": {
                    "supports": ["ProcessOrder"],
                    "usecases": ["SyncInventory"],
                    "description": "Inventory control",
                    "tags": {"tier": "infra"},
                },
            },
        })


@pytest.mark.pulse
class TestValidateSpecInvalid:
    def test_not_a_dict(self):
        with pytest.raises(PulseConfigError, match="must be a dict"):
            validate_spec("not a dict")

    def test_missing_schema_version(self):
        with pytest.raises(PulseConfigError, match="schema_version"):
            validate_spec({"value_tracks": {"x": {"usecases": ["A"]}}})

    def test_schema_version_not_string(self):
        with pytest.raises(PulseConfigError, match="must be a string"):
            validate_spec({"schema_version": 1, "value_tracks": {"x": {"usecases": ["A"]}}})

    def test_unsupported_schema_version(self):
        with pytest.raises(PulseConfigError, match="unsupported"):
            validate_spec({"schema_version": "99.0", "value_tracks": {"x": {"usecases": ["A"]}}})

    def test_missing_value_tracks(self):
        with pytest.raises(PulseConfigError, match="value_tracks"):
            validate_spec({"schema_version": "0.1"})

    def test_value_tracks_not_dict(self):
        with pytest.raises(PulseConfigError, match="must be a dict"):
            validate_spec({"schema_version": "0.1", "value_tracks": []})

    def test_value_tracks_empty(self):
        with pytest.raises(PulseConfigError, match="must not be empty"):
            validate_spec({"schema_version": "0.1", "value_tracks": {}})

    def test_track_not_dict(self):
        with pytest.raises(PulseConfigError, match="must be a dict"):
            validate_spec({"schema_version": "0.1", "value_tracks": {"core": "bad"}})

    def test_track_missing_usecases(self):
        with pytest.raises(PulseConfigError, match="usecases"):
            validate_spec({"schema_version": "0.1", "value_tracks": {"core": {}}})

    def test_usecases_not_list(self):
        with pytest.raises(PulseConfigError, match="must be a list"):
            validate_spec({
                "schema_version": "0.1",
                "value_tracks": {"core": {"usecases": "bad"}},
            })

    def test_usecases_empty(self):
        with pytest.raises(PulseConfigError, match="must not be empty"):
            validate_spec({
                "schema_version": "0.1",
                "value_tracks": {"core": {"usecases": []}},
            })

    def test_usecase_not_string(self):
        with pytest.raises(PulseConfigError, match="must be a string"):
            validate_spec({
                "schema_version": "0.1",
                "value_tracks": {"core": {"usecases": [123]}},
            })

    def test_subtracks_not_dict(self):
        spec = _minimal_spec()
        spec["value_tracks"]["core"]["subtracks"] = "bad"
        with pytest.raises(PulseConfigError, match="must be a dict"):
            validate_spec(spec)

    def test_subtrack_not_list(self):
        spec = _minimal_spec()
        spec["value_tracks"]["core"]["subtracks"] = {"sub": "bad"}
        with pytest.raises(PulseConfigError, match="must be a list"):
            validate_spec(spec)

    def test_subtrack_usecase_not_string(self):
        spec = _minimal_spec()
        spec["value_tracks"]["core"]["subtracks"] = {"sub": [123]}
        with pytest.raises(PulseConfigError, match="must be a string"):
            validate_spec(spec)

    def test_subtrack_references_unknown_usecase(self):
        spec = _minimal_spec()
        spec["value_tracks"]["core"]["subtracks"] = {"sub": ["NonExistent"]}
        with pytest.raises(PulseConfigError, match="unknown usecase"):
            validate_spec(spec)

    def test_tags_not_dict(self):
        spec = _minimal_spec()
        spec["value_tracks"]["core"]["tags"] = "bad"
        with pytest.raises(PulseConfigError, match="must be a dict"):
            validate_spec(spec)

    def test_tag_value_not_string(self):
        spec = _minimal_spec()
        spec["value_tracks"]["core"]["tags"] = {"tier": 123}
        with pytest.raises(PulseConfigError, match="must be a string"):
            validate_spec(spec)

    def test_description_not_string(self):
        spec = _minimal_spec()
        spec["value_tracks"]["core"]["description"] = 123
        with pytest.raises(PulseConfigError, match="must be a string"):
            validate_spec(spec)

    def test_duplicate_usecase_within_track(self):
        with pytest.raises(PulseConfigError, match="duplicate usecase 'CreateOrder'"):
            validate_spec({
                "schema_version": "0.1",
                "value_tracks": {
                    "core": {"usecases": ["CreateOrder", "CancelOrder", "CreateOrder"]},
                },
            })

    def test_support_tracks_in_v01_raises(self):
        with pytest.raises(PulseConfigError, match="requires schema_version"):
            validate_spec({
                "schema_version": "0.1",
                "value_tracks": {"core": {"usecases": ["A"]}},
                "support_tracks": {
                    "infra": {"supports": ["core"], "usecases": ["B"]},
                },
            })

    def test_support_tracks_not_dict_raises(self):
        with pytest.raises(PulseConfigError, match="must be a dict"):
            validate_spec({
                "schema_version": "0.2",
                "value_tracks": {"core": {"usecases": ["A"]}},
                "support_tracks": "bad",
            })

    def test_support_track_missing_usecases(self):
        with pytest.raises(PulseConfigError, match="missing required key 'usecases'"):
            validate_spec({
                "schema_version": "0.2",
                "value_tracks": {"core": {"usecases": ["A"]}},
                "support_tracks": {
                    "infra": {"supports": ["core"]},
                },
            })

    def test_support_track_empty_usecases(self):
        with pytest.raises(PulseConfigError, match="must not be empty"):
            validate_spec({
                "schema_version": "0.2",
                "value_tracks": {"core": {"usecases": ["A"]}},
                "support_tracks": {
                    "infra": {"supports": ["core"], "usecases": []},
                },
            })

    def test_support_track_missing_supports(self):
        with pytest.raises(PulseConfigError, match="missing required key 'supports'"):
            validate_spec({
                "schema_version": "0.2",
                "value_tracks": {"core": {"usecases": ["A"]}},
                "support_tracks": {
                    "infra": {"usecases": ["B"]},
                },
            })

    def test_support_track_empty_supports(self):
        with pytest.raises(PulseConfigError, match="must not be empty"):
            validate_spec({
                "schema_version": "0.2",
                "value_tracks": {"core": {"usecases": ["A"]}},
                "support_tracks": {
                    "infra": {"supports": [], "usecases": ["B"]},
                },
            })

    def test_support_track_supports_unknown_value_track(self):
        with pytest.raises(PulseConfigError, match="unknown value_track 'nonexistent'"):
            validate_spec({
                "schema_version": "0.2",
                "value_tracks": {"core": {"usecases": ["A"]}},
                "support_tracks": {
                    "infra": {"supports": ["nonexistent"], "usecases": ["B"]},
                },
            })

    def test_support_track_not_dict_raises(self):
        with pytest.raises(PulseConfigError, match="must be a dict"):
            validate_spec({
                "schema_version": "0.2",
                "value_tracks": {"core": {"usecases": ["A"]}},
                "support_tracks": {"infra": "bad"},
            })

    def test_support_track_usecases_not_list(self):
        with pytest.raises(PulseConfigError, match="must be a list"):
            validate_spec({
                "schema_version": "0.2",
                "value_tracks": {"core": {"usecases": ["A"]}},
                "support_tracks": {
                    "infra": {"supports": ["core"], "usecases": "bad"},
                },
            })

    def test_support_track_supports_not_list(self):
        with pytest.raises(PulseConfigError, match="must be a list"):
            validate_spec({
                "schema_version": "0.2",
                "value_tracks": {"core": {"usecases": ["A"]}},
                "support_tracks": {
                    "infra": {"supports": "core", "usecases": ["B"]},
                },
            })
