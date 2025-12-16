"""
Protocols for composition - low coupling interfaces.

Defines minimal interfaces that the composition system expects.
Allows injection of custom implementations for logging and metrics.

Author: ForgeBase Team
Created: 2025-12
"""

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class LoggerProtocol(Protocol):
    """
    Minimal interface for logging.

    Any object with these methods can be used as a logger.
    LogService from forge_base implements this interface.

    :Example:

        class MyLogger:
            def info(self, message: str, **kwargs): print(f"INFO: {message}")
            def warning(self, message: str, **kwargs): print(f"WARN: {message}")
            def error(self, message: str, **kwargs): print(f"ERROR: {message}")
            def debug(self, message: str, **kwargs): print(f"DEBUG: {message}")

        builder = MyBuilder(log=MyLogger())
    """

    def info(self, message: str, **kwargs: Any) -> None:
        """Log informational message."""
        ...

    def warning(self, message: str, **kwargs: Any) -> None:
        """Log warning message."""
        ...

    def error(self, message: str, **kwargs: Any) -> None:
        """Log error message."""
        ...

    def debug(self, message: str, **kwargs: Any) -> None:
        """Log debug message."""
        ...


@runtime_checkable
class MetricsProtocol(Protocol):
    """
    Minimal interface for metrics.

    Any object with these methods can be used for metrics collection.
    TrackMetrics from forge_base implements this interface.

    :Example:

        class MyMetrics:
            def increment(self, name: str, value: int = 1, **tags): pass
            def timing(self, name: str, value: float, **tags): pass

        builder = MyBuilder(metrics=MyMetrics())
    """

    def increment(self, name: str, value: int = 1, **tags: Any) -> None:
        """Increment a counter metric."""
        ...

    def timing(self, name: str, value: float, **tags: Any) -> None:
        """Record a timing metric."""
        ...
