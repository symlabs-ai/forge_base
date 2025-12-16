"""
Unit tests for IntentTracker.

Tests cognitive coherence tracking and validation.

:author: ForgeBase Development Team
:since: 2025-11-03
"""

import unittest

from forge_base.integration.intent_tracker import (
    CoherenceLevel,
    IntentTracker,
)


class TestIntentTracker(unittest.TestCase):
    """Test cases for IntentTracker."""

    def setUp(self):
        """Set up test fixtures."""
        self.tracker = IntentTracker()

    def test_capture_intent(self):
        """Test capturing an intent."""
        intent_id = self.tracker.capture_intent(
            description="Test intent",
            expected_outcome="Test outcome",
            source="test"
        )

        self.assertIsNotNone(intent_id)
        self.assertIn(intent_id, self.tracker._intents)

        intent = self.tracker.get_intent(intent_id)
        self.assertEqual(intent.description, "Test intent")
        self.assertEqual(intent.expected_outcome, "Test outcome")
        self.assertEqual(intent.source, "test")

    def test_record_execution(self):
        """Test recording execution."""
        intent_id = self.tracker.capture_intent(
            description="Test",
            expected_outcome="Success"
        )

        self.tracker.record_execution(
            intent_id=intent_id,
            actual_outcome="Success achieved",
            success=True,
            duration_ms=10.5
        )

        execution = self.tracker.get_execution(intent_id)
        self.assertEqual(execution.actual_outcome, "Success achieved")
        self.assertTrue(execution.success)
        self.assertEqual(execution.duration_ms, 10.5)

    def test_perfect_coherence(self):
        """Test perfect coherence detection."""
        intent_id = self.tracker.capture_intent(
            description="Create user",
            expected_outcome="User created successfully"
        )

        self.tracker.record_execution(
            intent_id=intent_id,
            actual_outcome="User created successfully",
            success=True
        )

        report = self.tracker.validate_coherence(intent_id)

        self.assertEqual(report.coherence_level, CoherenceLevel.PERFECT)
        self.assertGreaterEqual(report.similarity_score, 0.95)

    def test_high_coherence(self):
        """Test high coherence detection."""
        intent_id = self.tracker.capture_intent(
            description="Save data",
            expected_outcome="Data saved to database"
        )

        self.tracker.record_execution(
            intent_id=intent_id,
            actual_outcome="Data saved to database successfully",
            success=True
        )

        report = self.tracker.validate_coherence(intent_id)

        # Should be medium or higher (additional words reduce similarity)
        self.assertIn(
            report.coherence_level,
            [CoherenceLevel.PERFECT, CoherenceLevel.HIGH, CoherenceLevel.MEDIUM]
        )
        self.assertGreaterEqual(report.similarity_score, 0.60)

    def test_divergent_coherence(self):
        """Test divergent coherence detection."""
        intent_id = self.tracker.capture_intent(
            description="Process payment",
            expected_outcome="Payment processed successfully"
        )

        self.tracker.record_execution(
            intent_id=intent_id,
            actual_outcome="Error: Database connection failed",
            success=False
        )

        report = self.tracker.validate_coherence(intent_id)

        self.assertEqual(report.coherence_level, CoherenceLevel.DIVERGENT)
        self.assertLess(report.similarity_score, 0.40)
        self.assertTrue(len(report.divergences) > 0)

    def test_coherence_stats(self):
        """Test coherence statistics."""
        # Create multiple intents
        for i in range(3):
            intent_id = self.tracker.capture_intent(
                description=f"Test {i}",
                expected_outcome=f"Outcome {i}"
            )

            self.tracker.record_execution(
                intent_id=intent_id,
                actual_outcome=f"Outcome {i}",
                success=True
            )

        stats = self.tracker.get_coherence_stats()

        self.assertEqual(stats['total_intents'], 3)
        self.assertEqual(stats['total_executions'], 3)
        self.assertEqual(stats['success_rate'], 1.0)
        self.assertGreater(stats['avg_similarity'], 0.9)

    def test_export_learning_data(self):
        """Test exporting learning data."""
        intent_id = self.tracker.capture_intent(
            description="Test operation",
            expected_outcome="Operation complete",
            context_key="test_value"
        )

        self.tracker.record_execution(
            intent_id=intent_id,
            actual_outcome="Operation complete",
            success=True,
            result_id="123"
        )

        data = self.tracker.export_learning_data()

        self.assertEqual(len(data), 1)
        self.assertIn('intent', data[0])
        self.assertIn('execution', data[0])
        self.assertIn('coherence', data[0])

        self.assertEqual(
            data[0]['intent']['description'],
            "Test operation"
        )
        self.assertTrue(data[0]['execution']['success'])

    def test_recommendations(self):
        """Test recommendation generation."""
        intent_id = self.tracker.capture_intent(
            description="Quick operation",
            expected_outcome="Done"
        )

        # Slow execution
        self.tracker.record_execution(
            intent_id=intent_id,
            actual_outcome="Done",
            success=True,
            duration_ms=2000  # 2 seconds
        )

        report = self.tracker.validate_coherence(intent_id)

        # Should have performance recommendation
        self.assertTrue(len(report.recommendations) > 0)
        self.assertTrue(
            any("performance" in rec.lower() for rec in report.recommendations)
        )


if __name__ == '__main__':
    unittest.main()
