from types import MappingProxyType

import pytest

from forge_base.pulse.exceptions import PulseConfigError
from forge_base.pulse.support_tracks import SupportTrackMapping, SupportTrackRegistry


@pytest.mark.pulse
class TestSupportTrackMapping:
    def test_frozen(self):
        m = SupportTrackMapping(
            support_track="Infra", supports=("ProcessOrder",)
        )
        with pytest.raises(AttributeError):
            m.support_track = "other"  # type: ignore[misc]

    def test_defaults(self):
        m = SupportTrackMapping(
            support_track="Infra", supports=("ProcessOrder",)
        )
        assert m.description == ""
        assert m.tags == {}
        assert m.mapping_source == "spec"

    def test_custom_fields(self):
        m = SupportTrackMapping(
            support_track="Infra",
            supports=("ProcessOrder", "ManagePayments"),
            description="Infrastructure track",
            tags=MappingProxyType({"tier": "infra"}),
        )
        assert m.supports == ("ProcessOrder", "ManagePayments")
        assert m.description == "Infrastructure track"
        assert m.tags["tier"] == "infra"

    def test_supports_is_tuple(self):
        m = SupportTrackMapping(
            support_track="Infra", supports=("ProcessOrder",)
        )
        assert isinstance(m.supports, tuple)


@pytest.mark.pulse
class TestSupportTrackRegistry:
    def test_load_and_resolve(self):
        reg = SupportTrackRegistry()
        reg.load_from_dict({
            "schema_version": "0.2",
            "value_tracks": {
                "ProcessOrder": {"usecases": ["CreateOrder"]},
            },
            "support_tracks": {
                "ManageInventory": {
                    "supports": ["ProcessOrder"],
                    "usecases": ["SyncInventory", "ReserveStock"],
                },
            },
        })
        mapping = reg.resolve("SyncInventory")
        assert mapping is not None
        assert mapping.support_track == "ManageInventory"
        assert mapping.supports == ("ProcessOrder",)

    def test_resolve_second_usecase(self):
        reg = SupportTrackRegistry()
        reg.load_from_dict({
            "schema_version": "0.2",
            "value_tracks": {
                "ProcessOrder": {"usecases": ["CreateOrder"]},
            },
            "support_tracks": {
                "ManageInventory": {
                    "supports": ["ProcessOrder"],
                    "usecases": ["SyncInventory", "ReserveStock"],
                },
            },
        })
        mapping = reg.resolve("ReserveStock")
        assert mapping is not None
        assert mapping.support_track == "ManageInventory"

    def test_resolve_unknown_returns_none(self):
        reg = SupportTrackRegistry()
        reg.load_from_dict({
            "schema_version": "0.2",
            "value_tracks": {
                "ProcessOrder": {"usecases": ["CreateOrder"]},
            },
            "support_tracks": {
                "ManageInventory": {
                    "supports": ["ProcessOrder"],
                    "usecases": ["SyncInventory"],
                },
            },
        })
        assert reg.resolve("Unknown") is None

    def test_duplicate_usecase_raises(self):
        reg = SupportTrackRegistry()
        with pytest.raises(PulseConfigError, match="already mapped"):
            reg.load_from_dict({
                "schema_version": "0.2",
                "value_tracks": {
                    "ProcessOrder": {"usecases": ["CreateOrder"]},
                },
                "support_tracks": {
                    "TrackA": {
                        "supports": ["ProcessOrder"],
                        "usecases": ["SyncInventory"],
                    },
                    "TrackB": {
                        "supports": ["ProcessOrder"],
                        "usecases": ["SyncInventory"],
                    },
                },
            })

    def test_tags_and_description_propagated(self):
        reg = SupportTrackRegistry()
        reg.load_from_dict({
            "schema_version": "0.2",
            "value_tracks": {
                "ProcessOrder": {"usecases": ["CreateOrder"]},
            },
            "support_tracks": {
                "ManageInventory": {
                    "supports": ["ProcessOrder"],
                    "usecases": ["SyncInventory"],
                    "description": "Inventory control",
                    "tags": {"tier": "infra"},
                },
            },
        })
        mapping = reg.resolve("SyncInventory")
        assert mapping is not None
        assert mapping.description == "Inventory control"
        assert mapping.tags["tier"] == "infra"

    def test_no_support_tracks_in_spec(self):
        reg = SupportTrackRegistry()
        reg.load_from_dict({
            "schema_version": "0.2",
            "value_tracks": {
                "ProcessOrder": {"usecases": ["CreateOrder"]},
            },
        })
        assert reg.resolve("CreateOrder") is None

    def test_v01_spec_without_support_tracks(self):
        reg = SupportTrackRegistry()
        reg.load_from_dict({
            "schema_version": "0.1",
            "value_tracks": {
                "ProcessOrder": {"usecases": ["CreateOrder"]},
            },
        })
        assert reg.resolve("CreateOrder") is None

    def test_load_from_yaml(self, tmp_path):
        yaml_content = (
            "schema_version: '0.2'\n"
            "value_tracks:\n"
            "  ProcessOrder:\n"
            "    usecases:\n"
            "      - CreateOrder\n"
            "support_tracks:\n"
            "  ManageInventory:\n"
            "    supports:\n"
            "      - ProcessOrder\n"
            "    usecases:\n"
            "      - SyncInventory\n"
        )
        p = tmp_path / "spec.yaml"
        p.write_text(yaml_content)

        reg = SupportTrackRegistry()
        reg.load_from_yaml(p)
        mapping = reg.resolve("SyncInventory")
        assert mapping is not None
        assert mapping.support_track == "ManageInventory"

    def test_yaml_file_not_found(self):
        reg = SupportTrackRegistry()
        with pytest.raises(PulseConfigError, match="not found"):
            reg.load_from_yaml("/nonexistent/spec.yaml")

    def test_multiple_supports(self):
        reg = SupportTrackRegistry()
        reg.load_from_dict({
            "schema_version": "0.2",
            "value_tracks": {
                "ProcessOrder": {"usecases": ["CreateOrder"]},
                "ManagePayments": {"usecases": ["ChargeCard"]},
            },
            "support_tracks": {
                "AuditLog": {
                    "supports": ["ProcessOrder", "ManagePayments"],
                    "usecases": ["WriteAudit"],
                },
            },
        })
        mapping = reg.resolve("WriteAudit")
        assert mapping is not None
        assert mapping.supports == ("ProcessOrder", "ManagePayments")
