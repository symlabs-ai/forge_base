"""Tests for composition protocols."""

import pytest

from forge_base.composition.protocols import LoggerProtocol, MetricsProtocol


class FakeLogger:
    """Fake logger implementing LoggerProtocol."""

    def __init__(self) -> None:
        self.messages: list[tuple[str, str, dict]] = []

    def info(self, message: str, **kwargs) -> None:
        self.messages.append(("info", message, kwargs))

    def warning(self, message: str, **kwargs) -> None:
        self.messages.append(("warning", message, kwargs))

    def error(self, message: str, **kwargs) -> None:
        self.messages.append(("error", message, kwargs))

    def debug(self, message: str, **kwargs) -> None:
        self.messages.append(("debug", message, kwargs))


class FakeMetrics:
    """Fake metrics implementing MetricsProtocol."""

    def __init__(self) -> None:
        self.counters: dict[str, int] = {}
        self.timings: dict[str, float] = {}

    def increment(self, name: str, value: int = 1, **tags) -> None:
        self.counters[name] = self.counters.get(name, 0) + value

    def timing(self, name: str, value: float, **tags) -> None:
        self.timings[name] = value


class TestLoggerProtocol:
    """Tests for LoggerProtocol."""

    def test_fake_logger_implements_protocol(self) -> None:
        """FakeLogger should implement LoggerProtocol."""
        logger = FakeLogger()
        assert isinstance(logger, LoggerProtocol)

    def test_logger_info(self) -> None:
        """Logger info should record message."""
        logger = FakeLogger()
        logger.info("test message", key="value")
        assert len(logger.messages) == 1
        assert logger.messages[0] == ("info", "test message", {"key": "value"})

    def test_logger_warning(self) -> None:
        """Logger warning should record message."""
        logger = FakeLogger()
        logger.warning("warning message")
        assert logger.messages[0][0] == "warning"

    def test_logger_error(self) -> None:
        """Logger error should record message."""
        logger = FakeLogger()
        logger.error("error message")
        assert logger.messages[0][0] == "error"

    def test_logger_debug(self) -> None:
        """Logger debug should record message."""
        logger = FakeLogger()
        logger.debug("debug message")
        assert logger.messages[0][0] == "debug"


class TestMetricsProtocol:
    """Tests for MetricsProtocol."""

    def test_fake_metrics_implements_protocol(self) -> None:
        """FakeMetrics should implement MetricsProtocol."""
        metrics = FakeMetrics()
        assert isinstance(metrics, MetricsProtocol)

    def test_metrics_increment(self) -> None:
        """Metrics increment should increase counter."""
        metrics = FakeMetrics()
        metrics.increment("requests")
        assert metrics.counters["requests"] == 1

        metrics.increment("requests", 5)
        assert metrics.counters["requests"] == 6

    def test_metrics_timing(self) -> None:
        """Metrics timing should record value."""
        metrics = FakeMetrics()
        metrics.timing("response_time", 0.5)
        assert metrics.timings["response_time"] == 0.5
