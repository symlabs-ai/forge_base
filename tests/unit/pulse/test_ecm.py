import warnings

import pytest

from forge_base.pulse.ecm import (
    ExtensionCompatibilityMatrix,
    IncompatibleExtension,
    _parse_version,
    _satisfies,
)
from forge_base.pulse.exceptions import PulseConfigError, PulseIncompatibleExtensionError


@pytest.mark.pulse
class TestECMRegistration:
    def test_valid_registration(self):
        ecm = ExtensionCompatibilityMatrix()
        ecm.register_extension("my-ext", "1.0.0", "0.3")
        assert ecm.validate("0.3") == []

    def test_invalid_version_format(self):
        ecm = ExtensionCompatibilityMatrix()
        with pytest.raises(PulseConfigError, match="Invalid version"):
            ecm.register_extension("my-ext", "bad", "0.3")

    def test_invalid_requires_format(self):
        ecm = ExtensionCompatibilityMatrix()
        with pytest.raises(PulseConfigError, match="Invalid version"):
            ecm.register_extension("my-ext", "1.0.0", "abc")


@pytest.mark.pulse
class TestVersionParsing:
    def test_parse_major_minor(self):
        assert _parse_version("0.3") == (0, 3, 0)

    def test_parse_major_minor_patch(self):
        assert _parse_version("1.2.3") == (1, 2, 3)

    def test_satisfies_same_version(self):
        assert _satisfies("0.3.0", "0.3") is True

    def test_satisfies_higher_minor(self):
        assert _satisfies("0.4.0", "0.3") is True

    def test_not_satisfies_lower_minor(self):
        assert _satisfies("0.2.0", "0.3") is False

    def test_not_satisfies_different_major(self):
        assert _satisfies("1.3.0", "0.3") is False


@pytest.mark.pulse
class TestECMValidation:
    def test_compatible(self):
        ecm = ExtensionCompatibilityMatrix()
        ecm.register_extension("ext-a", "1.0.0", "0.3")
        assert ecm.validate("0.3") == []

    def test_incompatible_lower(self):
        ecm = ExtensionCompatibilityMatrix()
        ecm.register_extension("ext-a", "1.0.0", "0.4")
        result = ecm.validate("0.3")
        assert len(result) == 1
        assert result[0].name == "ext-a"
        assert result[0].requires_pulse == "0.4"

    def test_incompatible_different_major(self):
        ecm = ExtensionCompatibilityMatrix()
        ecm.register_extension("ext-a", "1.0.0", "1.0")
        result = ecm.validate("0.3")
        assert len(result) == 1

    def test_multiple_mixed(self):
        ecm = ExtensionCompatibilityMatrix()
        ecm.register_extension("ok-ext", "1.0.0", "0.3")
        ecm.register_extension("bad-ext", "2.0.0", "0.5")
        result = ecm.validate("0.3")
        assert len(result) == 1
        assert result[0].name == "bad-ext"

    def test_validate_or_raise_strict(self):
        ecm = ExtensionCompatibilityMatrix()
        ecm.register_extension("ext-a", "1.0.0", "0.5")
        with pytest.raises(PulseIncompatibleExtensionError, match="ext-a==1.0.0"):
            ecm.validate_or_raise("0.3")

    def test_validate_or_raise_ok(self):
        ecm = ExtensionCompatibilityMatrix()
        ecm.register_extension("ext-a", "1.0.0", "0.3")
        ecm.validate_or_raise("0.3")  # should not raise

    def test_validate_or_warn_emits(self):
        ecm = ExtensionCompatibilityMatrix()
        ecm.register_extension("ext-a", "1.0.0", "0.5")
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = ecm.validate_or_warn("0.3")
            assert len(w) == 1
            assert "ext-a" in str(w[0].message)
            assert issubclass(w[0].category, UserWarning)
        assert len(result) == 1

    def test_empty_ecm(self):
        ecm = ExtensionCompatibilityMatrix()
        assert ecm.validate("0.3") == []

    def test_incompatible_extension_frozen(self):
        ext = IncompatibleExtension(
            name="ext-a", version="1.0", requires_pulse="0.5", actual_pulse="0.3"
        )
        with pytest.raises(AttributeError):
            ext.name = "other"  # type: ignore[misc]
