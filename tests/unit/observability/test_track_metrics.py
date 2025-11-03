"""
Unit tests for TrackMetrics system.

:author: ForgeBase Development Team
:since: 2025-11-03
"""

import time
import unittest

from src.forgebase.observability.track_metrics import (
    TrackMetrics,
)


class TestTrackMetrics(unittest.TestCase):
    """Test suite for TrackMetrics."""

    def setUp(self):
        """Set up test fixtures."""
        self.metrics = TrackMetrics()

    def test_counter_increment(self):
        """Test incrementing a counter."""
        self.metrics.increment('requests.total')
        self.metrics.increment('requests.total')
        self.metrics.increment('requests.total')

        value = self.metrics.get_counter('requests.total')
        self.assertEqual(value, 3)

    def test_counter_with_custom_amount(self):
        """Test incrementing counter by custom amount."""
        self.metrics.increment('bytes.sent', amount=1024)
        self.metrics.increment('bytes.sent', amount=2048)

        value = self.metrics.get_counter('bytes.sent')
        self.assertEqual(value, 3072)

    def test_counter_with_labels(self):
        """Test counter with labels."""
        self.metrics.increment('requests.total', endpoint='/api/users', method='GET')
        self.metrics.increment('requests.total', endpoint='/api/users', method='POST')
        self.metrics.increment('requests.total', endpoint='/api/orders', method='GET')

        get_users = self.metrics.get_counter('requests.total', endpoint='/api/users', method='GET')
        post_users = self.metrics.get_counter('requests.total', endpoint='/api/users', method='POST')

        self.assertEqual(get_users, 1)
        self.assertEqual(post_users, 1)

    def test_gauge_set(self):
        """Test setting a gauge value."""
        self.metrics.gauge('memory.used_mb', 512.5)
        value = self.metrics.get_gauge('memory.used_mb')
        self.assertEqual(value, 512.5)

        # Gauge can be updated
        self.metrics.gauge('memory.used_mb', 1024.0)
        value = self.metrics.get_gauge('memory.used_mb')
        self.assertEqual(value, 1024.0)

    def test_histogram_observe(self):
        """Test observing values in histogram."""
        self.metrics.histogram('request.duration_ms', 100.0)
        self.metrics.histogram('request.duration_ms', 150.0)
        self.metrics.histogram('request.duration_ms', 200.0)

        stats = self.metrics.get_histogram_stats('request.duration_ms')

        self.assertEqual(stats['count'], 3)
        self.assertEqual(stats['min'], 100.0)
        self.assertEqual(stats['max'], 200.0)
        self.assertEqual(stats['mean'], 150.0)

    def test_histogram_percentiles(self):
        """Test histogram percentile calculations."""
        # Add 100 values
        for i in range(1, 101):
            self.metrics.histogram('latency_ms', float(i))

        stats = self.metrics.get_histogram_stats('latency_ms')

        self.assertEqual(stats['count'], 100)
        self.assertAlmostEqual(stats['p50'], 50, delta=5)
        self.assertAlmostEqual(stats['p95'], 95, delta=5)
        self.assertAlmostEqual(stats['p99'], 99, delta=5)

    def test_timer_context_manager(self):
        """Test timer context manager."""
        with self.metrics.timer('operation_duration_ms'):
            time.sleep(0.1)  # Sleep 100ms

        stats = self.metrics.get_histogram_stats('operation_duration_ms')

        self.assertIsNotNone(stats)
        self.assertEqual(stats['count'], 1)
        self.assertGreater(stats['mean'], 90)  # At least 90ms
        self.assertLess(stats['mean'], 200)  # Less than 200ms

    def test_timer_with_labels(self):
        """Test timer with labels."""
        with self.metrics.timer('query_duration_ms', database='postgres', operation='SELECT'):
            time.sleep(0.05)

        stats = self.metrics.get_histogram_stats('query_duration_ms', database='postgres', operation='SELECT')

        self.assertIsNotNone(stats)
        self.assertEqual(stats['count'], 1)

    def test_report_generation(self):
        """Test metrics report generation."""
        self.metrics.increment('requests.total')
        self.metrics.gauge('connections.active', 42)
        self.metrics.histogram('duration_ms', 123.5)

        report = self.metrics.report()

        self.assertIn('counters', report)
        self.assertIn('gauges', report)
        self.assertIn('histograms', report)
        self.assertIn('timestamp', report)

        self.assertEqual(report['counters']['requests.total'], 1)
        self.assertEqual(report['gauges']['connections.active'], 42)
        self.assertIn('duration_ms', report['histograms'])

    def test_reset_clears_metrics(self):
        """Test that reset clears all metrics."""
        self.metrics.increment('counter1')
        self.metrics.gauge('gauge1', 100)
        self.metrics.histogram('hist1', 50)

        report_before = self.metrics.report()
        self.assertGreater(len(report_before['counters']), 0)

        self.metrics.reset()

        report_after = self.metrics.report()
        self.assertEqual(len(report_after['counters']), 0)
        self.assertEqual(len(report_after['gauges']), 0)
        self.assertEqual(len(report_after['histograms']), 0)

    def test_nonexistent_metric_returns_none(self):
        """Test that accessing non-existent metric returns None."""
        counter_value = self.metrics.get_counter('nonexistent')
        gauge_value = self.metrics.get_gauge('nonexistent')
        histogram_stats = self.metrics.get_histogram_stats('nonexistent')

        self.assertIsNone(counter_value)
        self.assertIsNone(gauge_value)
        self.assertIsNone(histogram_stats)

    def test_repr(self):
        """Test string representation."""
        self.metrics.increment('test1')
        self.metrics.gauge('test2', 1)
        self.metrics.histogram('test3', 1)

        repr_str = repr(self.metrics)
        self.assertIn('TrackMetrics', repr_str)


if __name__ == '__main__':
    unittest.main()
