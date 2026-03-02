class PulseError(Exception):
    """Base exception for all pulse-related errors."""


class PulseConfigError(PulseError):
    """Raised when pulse configuration (spec YAML, registry setup) is invalid."""
