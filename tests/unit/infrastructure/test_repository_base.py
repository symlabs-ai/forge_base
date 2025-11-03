"""
Unit tests for RepositoryBase interface.

Tests the abstract repository interface using a concrete mock implementation
to verify the contract and expected behavior.

:author: ForgeBase Development Team
:since: 2025-11-03
"""

import unittest
from typing import Optional, List
from src.forgebase.domain.entity_base import EntityBase
from src.forgebase.infrastructure.repository.repository_base import RepositoryBase, RepositoryError


class MockEntity(EntityBase):
    """Mock entity for testing."""

    def __init__(self, id: Optional[str] = None, name: str = ""):
        super().__init__(id)
        self.name = name

    def validate(self) -> None:
        """Validate entity state."""
        if not self.name:
            raise ValueError("Name cannot be empty")


class InMemoryRepository(RepositoryBase[MockEntity]):
    """In-memory implementation of RepositoryBase for testing."""

    def __init__(self):
        self._storage: dict[str, MockEntity] = {}

    def save(self, entity: MockEntity) -> None:
        """Save entity to memory."""
        entity.validate()
        self._storage[entity.id] = entity

    def find_by_id(self, id: str) -> Optional[MockEntity]:
        """Find entity by ID."""
        return self._storage.get(id)

    def find_all(self) -> List[MockEntity]:
        """Find all entities."""
        return list(self._storage.values())

    def delete(self, id: str) -> None:
        """Delete entity by ID."""
        if id in self._storage:
            del self._storage[id]

    def exists(self, id: str) -> bool:
        """Check if entity exists."""
        return id in self._storage


class TestRepositoryBase(unittest.TestCase):
    """Test suite for RepositoryBase interface."""

    def setUp(self):
        """Set up test fixtures."""
        self.repository = InMemoryRepository()

    def test_save_entity(self):
        """Test saving an entity."""
        entity = MockEntity(name="Test Entity")

        self.repository.save(entity)

        saved = self.repository.find_by_id(entity.id)
        self.assertIsNotNone(saved)
        self.assertEqual(saved.id, entity.id)
        self.assertEqual(saved.name, "Test Entity")

    def test_save_updates_existing_entity(self):
        """Test that saving an existing entity updates it."""
        entity = MockEntity(name="Original")
        self.repository.save(entity)

        # Update and save again
        entity.name = "Updated"
        self.repository.save(entity)

        saved = self.repository.find_by_id(entity.id)
        self.assertEqual(saved.name, "Updated")

    def test_save_invalid_entity_raises_error(self):
        """Test that saving an invalid entity raises an error."""
        entity = MockEntity(name="")  # Invalid: empty name

        with self.assertRaises(ValueError):
            self.repository.save(entity)

    def test_find_by_id_returns_entity(self):
        """Test finding entity by ID."""
        entity = MockEntity(name="Findable")
        self.repository.save(entity)

        found = self.repository.find_by_id(entity.id)

        self.assertIsNotNone(found)
        self.assertEqual(found.id, entity.id)

    def test_find_by_id_returns_none_when_not_found(self):
        """Test that find_by_id returns None for non-existent ID."""
        result = self.repository.find_by_id("non-existent-id")

        self.assertIsNone(result)

    def test_find_all_returns_all_entities(self):
        """Test finding all entities."""
        entity1 = MockEntity(name="Entity 1")
        entity2 = MockEntity(name="Entity 2")
        entity3 = MockEntity(name="Entity 3")

        self.repository.save(entity1)
        self.repository.save(entity2)
        self.repository.save(entity3)

        all_entities = self.repository.find_all()

        self.assertEqual(len(all_entities), 3)
        entity_ids = [e.id for e in all_entities]
        self.assertIn(entity1.id, entity_ids)
        self.assertIn(entity2.id, entity_ids)
        self.assertIn(entity3.id, entity_ids)

    def test_find_all_returns_empty_list_when_empty(self):
        """Test that find_all returns empty list when repository is empty."""
        all_entities = self.repository.find_all()

        self.assertEqual(len(all_entities), 0)
        self.assertIsInstance(all_entities, list)

    def test_delete_removes_entity(self):
        """Test deleting an entity."""
        entity = MockEntity(name="To Delete")
        self.repository.save(entity)

        self.assertTrue(self.repository.exists(entity.id))

        self.repository.delete(entity.id)

        self.assertFalse(self.repository.exists(entity.id))
        self.assertIsNone(self.repository.find_by_id(entity.id))

    def test_delete_non_existent_entity_does_not_raise_error(self):
        """Test that deleting non-existent entity doesn't raise error."""
        # Should not raise exception
        self.repository.delete("non-existent-id")

    def test_exists_returns_true_when_entity_exists(self):
        """Test exists returns True for existing entity."""
        entity = MockEntity(name="Exists")
        self.repository.save(entity)

        self.assertTrue(self.repository.exists(entity.id))

    def test_exists_returns_false_when_entity_does_not_exist(self):
        """Test exists returns False for non-existent entity."""
        self.assertFalse(self.repository.exists("non-existent-id"))

    def test_repository_maintains_entity_references(self):
        """Test that repository maintains separate entity instances."""
        entity = MockEntity(name="Original")
        self.repository.save(entity)

        # Modify original entity
        entity.name = "Modified"

        # Retrieved entity should reflect the change (same instance in memory implementation)
        found = self.repository.find_by_id(entity.id)
        # Note: This behavior depends on implementation.
        # In this in-memory implementation, it's the same instance.
        # In real persistence, it would be a different instance.
        self.assertEqual(found.name, "Modified")

    def test_multiple_entities_can_coexist(self):
        """Test that multiple entities can be stored independently."""
        entity1 = MockEntity(name="Entity 1")
        entity2 = MockEntity(name="Entity 2")

        self.repository.save(entity1)
        self.repository.save(entity2)

        found1 = self.repository.find_by_id(entity1.id)
        found2 = self.repository.find_by_id(entity2.id)

        self.assertEqual(found1.name, "Entity 1")
        self.assertEqual(found2.name, "Entity 2")
        self.assertNotEqual(found1.id, found2.id)


class TestRepositoryError(unittest.TestCase):
    """Test suite for RepositoryError exception."""

    def test_repository_error_creation(self):
        """Test creating RepositoryError."""
        error = RepositoryError("Test error")
        self.assertEqual(str(error), "Test error")

    def test_repository_error_with_context(self):
        """Test RepositoryError with context information."""
        context = {"entity_id": "123", "operation": "save"}
        error = RepositoryError("Operation failed", context=context)

        self.assertEqual(str(error), "Operation failed")
        self.assertEqual(error.context, context)
        self.assertEqual(error.context["entity_id"], "123")

    def test_repository_error_is_exception(self):
        """Test that RepositoryError is an Exception."""
        error = RepositoryError("Test")
        self.assertIsInstance(error, Exception)


if __name__ == '__main__':
    unittest.main()
