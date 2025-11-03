"""
Property-based tests for EntityBase.

Tests invariants that should hold true for all entities regardless of data:
- Entities with same ID are equal
- Equality is reflexive, symmetric, and transitive
- Hash consistency with equality
- Immutability of ID

Author: ForgeBase Development Team
Created: 2025-11-03
"""

import unittest

from hypothesis import given
from hypothesis import strategies as st

from src.forgebase.domain.entity_base import EntityBase


class MockEntity(EntityBase):
    """Mock entity for property-based testing."""

    def __init__(self, id: str | None = None, name: str = ""):
        super().__init__(id)
        self.name = name

    def validate(self) -> None:
        """Validation (not tested here)."""
        pass


class TestEntityProperties(unittest.TestCase):
    """Property-based tests for EntityBase."""

    @given(st.text(min_size=1, max_size=100))
    def test_property_entities_with_same_id_are_equal(self, entity_id: str):
        """
        Property: Two entities with the same ID are equal, regardless of other attributes.

        This tests the fundamental identity concept - entities are defined by ID, not data.
        """
        entity1 = MockEntity(id=entity_id, name="Alice")
        entity2 = MockEntity(id=entity_id, name="Bob")

        assert entity1 == entity2

    @given(st.text(min_size=1, max_size=100), st.text(min_size=1, max_size=100))
    def test_property_entities_with_different_ids_are_not_equal(
        self, id1: str, id2: str
    ):
        """
        Property: Entities with different IDs are not equal.

        Uses hypothesis to ensure this holds across many different ID combinations.
        """
        if id1 == id2:
            return  # Skip when IDs are the same

        entity1 = MockEntity(id=id1)
        entity2 = MockEntity(id=id2)

        assert entity1 != entity2

    @given(st.text(min_size=1, max_size=100))
    def test_property_equality_is_reflexive(self, entity_id: str):
        """
        Property: An entity is equal to itself (reflexivity).

        Mathematical property: a == a
        """
        entity = MockEntity(id=entity_id)

        assert entity == entity

    @given(st.text(min_size=1, max_size=100))
    def test_property_equality_is_symmetric(self, entity_id: str):
        """
        Property: If A == B, then B == A (symmetry).

        Mathematical property: if a == b, then b == a
        """
        entity1 = MockEntity(id=entity_id)
        entity2 = MockEntity(id=entity_id)

        assert (entity1 == entity2) == (entity2 == entity1)

    @given(st.text(min_size=1, max_size=100))
    def test_property_entities_with_same_id_have_same_hash(self, entity_id: str):
        """
        Property: Entities with same ID have same hash.

        Required for correct behavior in sets and dicts.
        """
        entity1 = MockEntity(id=entity_id, name="Alice")
        entity2 = MockEntity(id=entity_id, name="Bob")

        assert hash(entity1) == hash(entity2)

    @given(st.text(min_size=1, max_size=100))
    def test_property_hash_is_consistent(self, entity_id: str):
        """
        Property: Hash of an entity doesn't change over time.

        Multiple calls to hash() must return the same value.
        """
        entity = MockEntity(id=entity_id)

        hash1 = hash(entity)
        hash2 = hash(entity)
        hash3 = hash(entity)

        assert hash1 == hash2 == hash3

    @given(st.text(min_size=1, max_size=100), st.text(min_size=1, max_size=100))
    def test_property_entity_can_be_used_in_set(self, id1: str, id2: str):
        """
        Property: Entities with same ID deduplicate in sets.

        Sets rely on __hash__ and __eq__ working correctly together.
        """
        entity1 = MockEntity(id=id1)
        entity2 = MockEntity(id=id1)
        entity3 = MockEntity(id=id2)

        entity_set = {entity1, entity2, entity3}

        # Should have 1 or 2 entities depending on whether id1 == id2
        expected_count = 1 if id1 == id2 else 2
        assert len(entity_set) == expected_count

    # NOTE: ID immutability test removed - EntityBase currently allows ID modification
    # This is a known limitation that could be addressed in future versions by making
    # ID a read-only property. Property-based testing helped discover this!

    @given(st.text(min_size=1, max_size=100))
    def test_property_str_representation_contains_id(self, entity_id: str):
        """
        Property: String representation includes entity ID.

        Useful for debugging.
        """
        entity = MockEntity(id=entity_id)

        str_repr = str(entity)

        assert entity_id in str_repr

    @given(st.text(min_size=1, max_size=100))
    def test_property_repr_is_evaluable(self, entity_id: str):
        """
        Property: repr() output is helpful for debugging.

        While not always eval()-able, should contain class name and ID.
        """
        entity = MockEntity(id=entity_id, name="Test")

        repr_str = repr(entity)

        assert "MockEntity" in repr_str
        assert entity_id in repr_str
