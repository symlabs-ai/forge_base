"""
Unit tests for EntityBase.

Tests validate the behavior of EntityBase according to Domain-Driven Design
principles, ensuring entities maintain correct identity semantics.

Author: Jorge, The Forge
Created: 2025-11-03
"""

import unittest
import uuid
from forgebase.domain.entity_base import EntityBase


class ConcreteEntity(EntityBase):
    """Concrete implementation of EntityBase for testing."""

    def __init__(self, id: str = None, name: str = ""):
        super().__init__(id)
        self.name = name

    def validate(self) -> None:
        """Validate that name is not empty."""
        if not self.name:
            raise ValueError("Name cannot be empty")


class TestEntityBase(unittest.TestCase):
    """Test suite for EntityBase class."""

    def test_entity_with_provided_id(self):
        """Test that entity uses provided ID."""
        entity_id = "test-entity-123"
        entity = ConcreteEntity(id=entity_id, name="Test")

        self.assertEqual(entity.id, entity_id)

    def test_entity_with_auto_generated_id(self):
        """Test that entity auto-generates ID when not provided."""
        entity = ConcreteEntity(name="Test")

        self.assertIsNotNone(entity.id)
        self.assertIsInstance(entity.id, str)
        # Validate it's a valid UUID
        try:
            uuid.UUID(entity.id)
        except ValueError:
            self.fail(f"Generated ID '{entity.id}' is not a valid UUID")

    def test_auto_generated_ids_are_unique(self):
        """Test that auto-generated IDs are unique across entities."""
        entity1 = ConcreteEntity(name="Entity1")
        entity2 = ConcreteEntity(name="Entity2")
        entity3 = ConcreteEntity(name="Entity3")

        ids = {entity1.id, entity2.id, entity3.id}
        self.assertEqual(len(ids), 3, "Generated IDs should be unique")

    def test_entity_equality_by_id(self):
        """Test that entities with same ID are considered equal."""
        entity_id = "same-id"
        entity1 = ConcreteEntity(id=entity_id, name="Name1")
        entity2 = ConcreteEntity(id=entity_id, name="Name2")

        self.assertEqual(entity1, entity2)

    def test_entity_inequality_different_ids(self):
        """Test that entities with different IDs are not equal."""
        entity1 = ConcreteEntity(id="id-1", name="Same Name")
        entity2 = ConcreteEntity(id="id-2", name="Same Name")

        self.assertNotEqual(entity1, entity2)

    def test_entity_not_equal_to_non_entity(self):
        """Test that entity is not equal to non-entity objects."""
        entity = ConcreteEntity(id="test-id", name="Test")

        self.assertNotEqual(entity, "test-id")
        self.assertNotEqual(entity, 123)
        self.assertNotEqual(entity, None)
        self.assertNotEqual(entity, {"id": "test-id"})

    def test_entity_hash_based_on_id(self):
        """Test that entity hash is based on ID."""
        entity_id = "test-id"
        entity = ConcreteEntity(id=entity_id, name="Test")

        self.assertEqual(hash(entity), hash(entity_id))

    def test_entities_with_same_id_have_same_hash(self):
        """Test that entities with same ID have same hash."""
        entity_id = "same-id"
        entity1 = ConcreteEntity(id=entity_id, name="Name1")
        entity2 = ConcreteEntity(id=entity_id, name="Name2")

        self.assertEqual(hash(entity1), hash(entity2))

    def test_entity_can_be_used_in_set(self):
        """Test that entities can be stored in sets."""
        entity1 = ConcreteEntity(id="id-1", name="Entity1")
        entity2 = ConcreteEntity(id="id-2", name="Entity2")
        entity3 = ConcreteEntity(id="id-1", name="Entity1 Updated")

        entity_set = {entity1, entity2, entity3}

        # entity3 has same ID as entity1, so should not be added
        self.assertEqual(len(entity_set), 2)
        self.assertIn(entity1, entity_set)
        self.assertIn(entity2, entity_set)

    def test_entity_can_be_used_as_dict_key(self):
        """Test that entities can be used as dictionary keys."""
        entity1 = ConcreteEntity(id="id-1", name="Entity1")
        entity2 = ConcreteEntity(id="id-2", name="Entity2")

        entity_dict = {
            entity1: "Value1",
            entity2: "Value2"
        }

        self.assertEqual(entity_dict[entity1], "Value1")
        self.assertEqual(entity_dict[entity2], "Value2")

    def test_validate_is_abstract(self):
        """Test that EntityBase.validate() is abstract."""
        # EntityBase itself cannot be instantiated
        with self.assertRaises(TypeError):
            # This should fail because validate() is abstract
            entity = EntityBase()  # type: ignore

    def test_validate_called_raises_on_invalid(self):
        """Test that validate() raises exception for invalid entity."""
        entity = ConcreteEntity(name="")  # Empty name

        with self.assertRaises(ValueError) as context:
            entity.validate()

        self.assertIn("Name cannot be empty", str(context.exception))

    def test_validate_passes_for_valid_entity(self):
        """Test that validate() doesn't raise for valid entity."""
        entity = ConcreteEntity(name="Valid Name")

        try:
            entity.validate()
        except Exception as e:
            self.fail(f"validate() raised {e} unexpectedly")

    def test_repr_contains_class_and_id(self):
        """Test that __repr__ returns meaningful representation."""
        entity = ConcreteEntity(id="test-id-123", name="Test")

        repr_str = repr(entity)

        self.assertIn("ConcreteEntity", repr_str)
        self.assertIn("test-id-123", repr_str)

    def test_str_returns_useful_representation(self):
        """Test that __str__ returns useful representation."""
        entity = ConcreteEntity(id="test-id-456", name="Test")

        str_repr = str(entity)

        self.assertIsInstance(str_repr, str)
        self.assertIn("ConcreteEntity", str_repr)
        self.assertIn("test-id-456", str_repr)

    def test_entity_identity_preserved_through_attribute_changes(self):
        """Test that entity identity is preserved when attributes change."""
        entity_id = "stable-id"
        entity = ConcreteEntity(id=entity_id, name="Original Name")
        original_hash = hash(entity)

        # Store in set
        entity_set = {entity}

        # Change attribute
        entity.name = "Updated Name"

        # Identity should be preserved
        self.assertEqual(entity.id, entity_id)
        self.assertEqual(hash(entity), original_hash)
        self.assertIn(entity, entity_set)

    def test_different_entity_types_with_same_id_are_equal(self):
        """Test that different entity types with same ID are considered equal."""
        class OtherEntity(EntityBase):
            def validate(self):
                pass

        entity_id = "shared-id"
        entity1 = ConcreteEntity(id=entity_id, name="Test")
        entity2 = OtherEntity(id=entity_id)

        # Both are EntityBase instances with same ID
        self.assertEqual(entity1, entity2)


if __name__ == "__main__":
    unittest.main()
