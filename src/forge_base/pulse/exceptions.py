class PulseError(Exception):
    """Base exception for all pulse-related errors."""


class PulseConfigError(PulseError):
    """Raised when pulse configuration (spec YAML, registry setup) is invalid."""


class PulseIncompatibleExtensionError(PulseError):
    """Raised when a CE extension is incompatible with the current Pulse version."""
