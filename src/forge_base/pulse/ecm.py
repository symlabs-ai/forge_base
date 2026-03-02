from __future__ import annotations

from dataclasses import dataclass
import re
import warnings

from forge_base.pulse.exceptions import PulseConfigError, PulseIncompatibleExtensionError

_SEMVER_RE = re.compile(r"^(\d+)\.(\d+)(?:\.(\d+))?$")


def _parse_version(version: str) -> tuple[int, int, int]:
    """Parse a version string into (major, minor, patch)."""
    m = _SEMVER_RE.match(version)
    if m is None:
        raise PulseConfigError(f"Invalid version format: {version!r}")
    return int(m.group(1)), int(m.group(2)), int(m.group(3) or 0)


def _satisfies(actual: str, required: str) -> bool:
    """Check if actual version satisfies required (same major, actual >= required)."""
    actual_t = _parse_version(actual)
    required_t = _parse_version(required)
    if actual_t[0] != required_t[0]:
        return False
    return actual_t >= required_t


@dataclass(frozen=True)
class IncompatibleExtension:
    """Record of an extension that failed compatibility check."""

    name: str
    version: str
    requires_pulse: str
    actual_pulse: str


class ExtensionCompatibilityMatrix:
    """Validates CE extension compatibility with the current Pulse version."""

    __slots__ = ("_extensions",)

    def __init__(self) -> None:
        self._extensions: list[tuple[str, str, str]] = []

    def register_extension(self, name: str, version: str, requires_pulse: str) -> None:
        """Register an extension with its version and required Pulse version.

        Validates version formats eagerly on registration.
        """
        _parse_version(version)
        _parse_version(requires_pulse)
        self._extensions.append((name, version, requires_pulse))

    def validate(self, pulse_version: str) -> list[IncompatibleExtension]:
        """Return list of incompatible extensions for the given Pulse version."""
        _parse_version(pulse_version)
        incompatible: list[IncompatibleExtension] = []
        for name, version, requires_pulse in self._extensions:
            if not _satisfies(pulse_version, requires_pulse):
                incompatible.append(
                    IncompatibleExtension(
                        name=name,
                        version=version,
                        requires_pulse=requires_pulse,
                        actual_pulse=pulse_version,
                    )
                )
        return incompatible

    def validate_or_raise(self, pulse_version: str) -> None:
        """Raise PulseIncompatibleExtensionError if any extension is incompatible."""
        incompatible = self.validate(pulse_version)
        if incompatible:
            names = ", ".join(f"{e.name}=={e.version}" for e in incompatible)
            raise PulseIncompatibleExtensionError(
                f"Incompatible extensions: {names}"
            )

    def validate_or_warn(self, pulse_version: str) -> list[IncompatibleExtension]:
        """Emit UserWarning for each incompatible extension and return them."""
        incompatible = self.validate(pulse_version)
        for ext in incompatible:
            warnings.warn(
                f"Extension {ext.name}=={ext.version} requires pulse>={ext.requires_pulse}, "
                f"but current is {ext.actual_pulse}",
                UserWarning,
                stacklevel=2,
            )
        return incompatible
