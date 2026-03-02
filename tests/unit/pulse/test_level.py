import pytest

from forge_base.pulse.level import MonitoringLevel


@pytest.mark.pulse
class TestMonitoringLevel:
    def test_values(self):
        assert MonitoringLevel.OFF == 0
        assert MonitoringLevel.BASIC == 10
        assert MonitoringLevel.STANDARD == 20
        assert MonitoringLevel.DETAILED == 30
        assert MonitoringLevel.DIAGNOSTIC == 40

    def test_ordering(self):
        assert MonitoringLevel.OFF < MonitoringLevel.BASIC
        assert MonitoringLevel.BASIC < MonitoringLevel.STANDARD
        assert MonitoringLevel.STANDARD < MonitoringLevel.DETAILED
        assert MonitoringLevel.DETAILED < MonitoringLevel.DIAGNOSTIC

    def test_is_int_enum(self):
        assert isinstance(MonitoringLevel.OFF, int)

    def test_all_members(self):
        names = [m.name for m in MonitoringLevel]
        assert names == ["OFF", "BASIC", "STANDARD", "DETAILED", "DIAGNOSTIC"]

    def test_comparable_to_int(self):
        assert MonitoringLevel.BASIC > 5
        assert MonitoringLevel.OFF == 0
