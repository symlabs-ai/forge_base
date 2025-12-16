"""
Tests for ForgeTestCase.

Meta-tests: testing the test infrastructure itself!

:author: ForgeBase Development Team
:since: 2025-11-03
"""

import unittest

from src.forge_base.testing.forge_test_case import ForgeTestCase


class TestForgeTestCase(ForgeTestCase):
    """Test the ForgeTestCase base class."""

    def test_setup_context(self):
        """Test context setup and retrieval."""
        self.setup_context(user_id="test-123", tenant="test-tenant")

        assert self.get_context("user_id") == "test-123"
        assert self.get_context("tenant") == "test-tenant"
        assert self.get_context("nonexistent") is None
        assert self.get_context("nonexistent", "default") == "default"

    def test_assert_intent_matches_success(self):
        """Test successful intent matching."""
        self.assert_intent_matches(
            expected_intent="Store user in database",
            actual="Store user in database successfully",
            threshold=0.7
        )

    def test_assert_intent_matches_failure(self):
        """Test intent matching failure."""
        with self.assertRaises(AssertionError):
            self.assert_intent_matches(
                expected_intent="Delete user",
                actual="User was created"
            )

    def test_capture_and_assert_metrics(self):
        """Test metric capture and assertion."""
        self.capture_metric('test.counter', 5)
        self.capture_metric('test.gauge', 42.5)

        self.assert_metrics_collected({
            'test.counter': 5,
            'test.gauge': 42.5,
        })

    def test_assert_metrics_with_callable(self):
        """Test metric assertion with callable validator."""
        self.capture_metric('test.value', 100)

        self.assert_metrics_collected({
            'test.value': lambda x: x > 50
        })

    def test_assert_no_side_effects(self):
        """Test side effect detection."""
        obj = type('TestObject', (), {'value': 10, 'name': 'test'})()

        # No mutation - should pass
        with self.assert_no_side_effects(obj):
            _ = obj.value * 2

        # Mutation - should fail
        with self.assertRaises(AssertionError), self.assert_no_side_effects(obj):
            obj.value = 20

    def test_assert_no_side_effects_with_exceptions(self):
        """Test side effect detection with allowed mutations."""
        obj = type('TestObject', (), {'value': 10, 'storage': []})()

        # Allow storage mutation
        with self.assert_no_side_effects(obj, except_mutations=['storage']):
            obj.storage.append(1)  # Allowed
            # obj.value = 20  # Would fail


if __name__ == '__main__':
    unittest.main()
