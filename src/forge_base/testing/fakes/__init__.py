"""
Test doubles and fakes for ForgeBase testing.

This package provides fake implementations of core interfaces for testing:
- FakeLogger: In-memory logger
- FakeRepository: In-memory repository
- FakeMetricsCollector: In-memory metrics collector

:author: ForgeBase Development Team
:since: 2025-11-03
"""

from forge_base.testing.fakes.fake_logger import FakeLogger
from forge_base.testing.fakes.fake_metrics_collector import FakeMetricsCollector
from forge_base.testing.fakes.fake_repository import FakeRepository

__all__ = [
    'FakeLogger',
    'FakeRepository',
    'FakeMetricsCollector',
]
