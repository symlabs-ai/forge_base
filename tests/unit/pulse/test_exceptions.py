import pytest

from forge_base.pulse.exceptions import PulseConfigError, PulseError


@pytest.mark.pulse
class TestPulseExceptions:
    def test_pulse_error_is_exception(self):
        assert issubclass(PulseError, Exception)

    def test_pulse_config_error_is_pulse_error(self):
        assert issubclass(PulseConfigError, PulseError)

    def test_pulse_config_error_is_exception(self):
        assert issubclass(PulseConfigError, Exception)

    def test_pulse_error_catchable_as_exception(self):
        with pytest.raises(PulseError):
            raise PulseError("test")

    def test_pulse_config_error_catchable_as_pulse_error(self):
        with pytest.raises(PulseError):
            raise PulseConfigError("bad config")

    def test_pulse_error_message(self):
        err = PulseError("something went wrong")
        assert str(err) == "something went wrong"

    def test_pulse_config_error_message(self):
        err = PulseConfigError("invalid spec")
        assert str(err) == "invalid spec"

    def test_reexported_from_pulse_init(self):
        from forge_base.pulse import PulseConfigError as Reexported
        from forge_base.pulse import PulseError as ReexportedBase

        assert ReexportedBase is PulseError
        assert Reexported is PulseConfigError
