from types import MappingProxyType

import pytest

from forge_base.pulse.exceptions import PulseConfigError
from forge_base.pulse.value_tracks import ValueTrackMapping, ValueTrackRegistry


def _spec_dict(**overrides):
    base = {
        "schema_version": "0.1",
        "value_tracks": {
            "core": {
                "usecases": ["CreateOrder", "CancelOrder"],
                "subtracks": {"checkout": ["CreateOrder"]},
                "tags": {"tier": "premium"},
            },
        },
    }
    base.update(overrides)
    return base


@pytest.mark.pulse
class TestValueTrackMapping:
    def test_frozen(self):
        m = ValueTrackMapping(value_track="core")
        with pytest.raises(AttributeError):
            m.value_track = "other"

    def test_defaults(self):
        m = ValueTrackMapping(value_track="core")
        assert m.subtrack == ""
        assert m.tags == MappingProxyType({})
        assert m.mapping_source == "spec"

    def test_tags_immutable(self):
        m = ValueTrackMapping(value_track="core", tags=MappingProxyType({"a": "b"}))
        with pytest.raises(TypeError):
            m.tags["new"] = "val"


@pytest.mark.pulse
class TestValueTrackRegistry:
    def test_load_from_dict(self):
        reg = ValueTrackRegistry()
        reg.load_from_dict(_spec_dict())
        assert reg.resolve("CreateOrder") is not None
        assert reg.resolve("CancelOrder") is not None

    def test_resolve_mapped_usecase(self):
        reg = ValueTrackRegistry()
        reg.load_from_dict(_spec_dict())
        m = reg.resolve("CreateOrder")
        assert m is not None
        assert m.value_track == "core"
        assert m.subtrack == "checkout"
        assert m.tags == MappingProxyType({"tier": "premium"})
        assert m.mapping_source == "spec"

    def test_resolve_mapped_without_subtrack(self):
        reg = ValueTrackRegistry()
        reg.load_from_dict(_spec_dict())
        m = reg.resolve("CancelOrder")
        assert m is not None
        assert m.value_track == "core"
        assert m.subtrack == ""

    def test_resolve_unmapped_returns_none(self):
        reg = ValueTrackRegistry()
        reg.load_from_dict(_spec_dict())
        assert reg.resolve("UnknownUseCase") is None

    def test_duplicate_usecase_raises(self):
        spec = {
            "schema_version": "0.1",
            "value_tracks": {
                "core": {"usecases": ["CreateOrder"]},
                "support": {"usecases": ["CreateOrder"]},
            },
        }
        reg = ValueTrackRegistry()
        with pytest.raises(PulseConfigError, match="already mapped"):
            reg.load_from_dict(spec)

    def test_load_from_yaml(self, tmp_path):
        yaml_content = (
            "schema_version: '0.1'\n"
            "value_tracks:\n"
            "  core:\n"
            "    usecases:\n"
            "      - CreateOrder\n"
        )
        p = tmp_path / "spec.yaml"
        p.write_text(yaml_content)

        reg = ValueTrackRegistry()
        reg.load_from_yaml(p)
        assert reg.resolve("CreateOrder") is not None

    def test_load_from_yaml_file_not_found(self):
        reg = ValueTrackRegistry()
        with pytest.raises(PulseConfigError, match="not found"):
            reg.load_from_yaml("/nonexistent/spec.yaml")

    def test_load_from_yaml_empty_file(self, tmp_path):
        p = tmp_path / "empty.yaml"
        p.write_text("")
        reg = ValueTrackRegistry()
        with pytest.raises(PulseConfigError, match="empty"):
            reg.load_from_yaml(p)

    def test_multiple_tracks(self):
        spec = {
            "schema_version": "0.1",
            "value_tracks": {
                "core": {"usecases": ["CreateOrder"]},
                "support": {"usecases": ["TicketReply"]},
            },
        }
        reg = ValueTrackRegistry()
        reg.load_from_dict(spec)
        assert reg.resolve("CreateOrder").value_track == "core"
        assert reg.resolve("TicketReply").value_track == "support"

    def test_empty_registry_resolve_returns_none(self):
        reg = ValueTrackRegistry()
        assert reg.resolve("Anything") is None

    def test_load_from_yaml_accepts_string_path(self, tmp_path):
        yaml_content = (
            "schema_version: '0.1'\n"
            "value_tracks:\n"
            "  core:\n"
            "    usecases:\n"
            "      - DoStuff\n"
        )
        p = tmp_path / "spec.yaml"
        p.write_text(yaml_content)

        reg = ValueTrackRegistry()
        reg.load_from_yaml(str(p))
        assert reg.resolve("DoStuff") is not None

    def test_tags_empty_when_not_specified(self):
        spec = {
            "schema_version": "0.1",
            "value_tracks": {
                "core": {"usecases": ["CreateOrder"]},
            },
        }
        reg = ValueTrackRegistry()
        reg.load_from_dict(spec)
        m = reg.resolve("CreateOrder")
        assert m.tags == MappingProxyType({})

    def test_load_from_yaml_malformed_raises_config_error(self, tmp_path):
        p = tmp_path / "bad.yaml"
        p.write_text("value_tracks:\n  core:\n    usecases:\n  - broken indent")
        reg = ValueTrackRegistry()
        with pytest.raises(PulseConfigError, match="invalid YAML"):
            reg.load_from_yaml(p)
