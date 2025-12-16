"""
Property-based tests for ValueObjectBase.

Tests invariants for value objects:
- Structural equality (equal values = equal objects)
- Immutability after freezing
- Hash consistency
- Value semantics

Author: ForgeBase Development Team
Created: 2025-11-03
"""

import unittest

from hypothesis import given
from hypothesis import strategies as st

from src.forge_base.domain.value_object_base import ValueObjectBase


class MockValueObject(ValueObjectBase):
    """Mock value object for property-based testing."""

    def __init__(self, value: str, count: int):
        super().__init__()
        self.value = value
        self.count = count
        self._freeze()

    def validate(self) -> None:
        """Validation (not tested here)."""
        pass


class TestValueObjectProperties(unittest.TestCase):
    """Property-based tests for ValueObjectBase."""

    @given(st.text(min_size=0, max_size=100), st.integers(min_value=0, max_value=1000))
    def test_property_value_objects_with_same_attributes_are_equal(
        self, value: str, count: int
    ):
        """
        Property: Value objects with same attributes are equal.

        Unlike entities, value objects are defined by their data, not identity.
        """
        vo1 = MockValueObject(value, count)
        vo2 = MockValueObject(value, count)

        assert vo1 == vo2

    @given(
        st.text(min_size=0, max_size=100),
        st.text(min_size=0, max_size=100),
        st.integers(min_value=0, max_value=1000),
    )
    def test_property_value_objects_with_different_attributes_are_not_equal(
        self, value1: str, value2: str, count: int
    ):
        """
        Property: Value objects with different data are not equal.
        """
        if value1 == value2:
            return  # Skip when values are the same

        vo1 = MockValueObject(value1, count)
        vo2 = MockValueObject(value2, count)

        assert vo1 != vo2

    @given(st.text(min_size=0, max_size=100), st.integers(min_value=0, max_value=1000))
    def test_property_equality_is_reflexive(self, value: str, count: int):
        """
        Property: A value object is equal to itself.
        """
        vo = MockValueObject(value, count)

        assert vo == vo

    @given(st.text(min_size=0, max_size=100), st.integers(min_value=0, max_value=1000))
    def test_property_equality_is_symmetric(self, value: str, count: int):
        """
        Property: If A == B, then B == A.
        """
        vo1 = MockValueObject(value, count)
        vo2 = MockValueObject(value, count)

        assert (vo1 == vo2) == (vo2 == vo1)

    @given(st.text(min_size=0, max_size=100), st.integers(min_value=0, max_value=1000))
    def test_property_same_values_produce_same_hash(self, value: str, count: int):
        """
        Property: Value objects with same data have same hash.

        Required for use in sets and dict keys.
        """
        vo1 = MockValueObject(value, count)
        vo2 = MockValueObject(value, count)

        assert hash(vo1) == hash(vo2)

    @given(st.text(min_size=0, max_size=100), st.integers(min_value=0, max_value=1000))
    def test_property_hash_is_consistent(self, value: str, count: int):
        """
        Property: Hash doesn't change over time.
        """
        vo = MockValueObject(value, count)

        hash1 = hash(vo)
        hash2 = hash(vo)
        hash3 = hash(vo)

        assert hash1 == hash2 == hash3

    @given(st.text(min_size=0, max_size=100), st.integers(min_value=0, max_value=1000))
    def test_property_value_object_is_immutable(self, value: str, count: int):
        """
        Property: Value objects cannot be modified after creation.

        Immutability is fundamental to value objects.
        """
        vo = MockValueObject(value, count)

        with self.assertRaises(AttributeError):
            vo.value = "new value"

        with self.assertRaises(AttributeError):
            vo.count = 999

    @given(
        st.text(min_size=0, max_size=100),
        st.text(min_size=0, max_size=100),
        st.integers(min_value=0, max_value=1000),
    )
    def test_property_value_objects_can_be_used_in_set(
        self, value1: str, value2: str, count: int
    ):
        """
        Property: Value objects with same data deduplicate in sets.
        """
        vo1 = MockValueObject(value1, count)
        vo2 = MockValueObject(value1, count)
        vo3 = MockValueObject(value2, count)

        vo_set = {vo1, vo2, vo3}

        # Should have 1 or 2 depending on whether value1 == value2
        expected_count = 1 if value1 == value2 else 2
        assert len(vo_set) == expected_count

    @given(st.text(min_size=0, max_size=100), st.integers(min_value=0, max_value=1000))
    def test_property_to_dict_returns_all_non_private_attributes(
        self, value: str, count: int
    ):
        """
        Property: to_dict() includes all non-private attributes.
        """
        vo = MockValueObject(value, count)

        d = vo.to_dict()

        assert "value" in d
        assert "count" in d
        assert d["value"] == value
        assert d["count"] == count
        assert "_frozen" not in d  # Private attributes excluded

    @given(st.text(min_size=0, max_size=100), st.integers(min_value=0, max_value=1000))
    def test_property_repr_contains_attributes(self, value: str, count: int):
        """
        Property: repr() output contains class name and attributes.
        """
        vo = MockValueObject(value, count)

        repr_str = repr(vo)

        assert "MockValueObject" in repr_str
        # Values might be truncated/escaped, so just check structure
        assert "value=" in repr_str or "count=" in repr_str
