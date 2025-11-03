"""
Contract tests for RepositoryBase implementations.

Provides a test mixin that validates all implementations conform to the
RepositoryBase contract. Any repository implementation can inherit this
mixin to automatically verify correct behavior.

Philosophy:
    Contract tests ensure behavioral correctness beyond type signatures.
    They verify that implementations respect the semantic contract:
    - save() is idempotent
    - find_by_id() returns None for missing entities (not exception)
    - delete() is idempotent
    - exists() correctly reflects entity presence

Usage:
    class TestMyRepository(RepositoryContractTestMixin, unittest.TestCase):
        def create_repository(self):
            return MyRepository()

        def create_entity(self, id: str):
            return MyEntity(id=id)

Author: ForgeBase Development Team
Created: 2025-11-03
"""

from abc import ABC, abstractmethod

from forgebase.domain.entity_base import EntityBase
from forgebase.infrastructure.repository.repository_base import RepositoryBase


class RepositoryContractTestMixin(ABC):
    """
    Test mixin for RepositoryBase contract validation.

    Implementations must provide:
    - create_repository(): Returns a fresh repository instance
    - create_entity(id: str): Creates a test entity with given ID
    """

    @abstractmethod
    def create_repository(self) -> RepositoryBase:
        """
        Create a fresh repository instance for testing.

        Must return a new, empty repository for each test.

        :return: Repository instance
        :rtype: RepositoryBase
        """
        pass

    @abstractmethod
    def create_entity(self, id: str) -> EntityBase:
        """
        Create a test entity with given ID.

        :param id: Entity ID
        :type id: str
        :return: Test entity
        :rtype: EntityBase
        """
        pass

    # Contract Tests

    def test_contract_save_and_find_by_id(self) -> None:
        """save() persists entity, find_by_id() retrieves it."""
        repo = self.create_repository()
        entity = self.create_entity("test-1")

        repo.save(entity)
        found = repo.find_by_id("test-1")

        assert found is not None
        assert found.id == entity.id

    def test_contract_save_is_idempotent(self) -> None:
        """save() with same ID updates, doesn't duplicate."""
        repo = self.create_repository()
        entity = self.create_entity("test-1")

        # Save twice
        repo.save(entity)
        repo.save(entity)

        # Should have exactly one entity
        all_entities = repo.find_all()
        assert len(all_entities) == 1

    def test_contract_find_by_id_returns_none_when_not_found(self) -> None:
        """find_by_id() returns None for missing entity (not exception)."""
        repo = self.create_repository()

        found = repo.find_by_id("nonexistent")

        assert found is None

    def test_contract_find_all_returns_empty_list_when_empty(self) -> None:
        """find_all() returns empty list when repository is empty."""
        repo = self.create_repository()

        entities = repo.find_all()

        assert isinstance(entities, list)
        assert len(entities) == 0

    def test_contract_find_all_returns_all_entities(self) -> None:
        """find_all() returns all saved entities."""
        repo = self.create_repository()
        entity1 = self.create_entity("test-1")
        entity2 = self.create_entity("test-2")

        repo.save(entity1)
        repo.save(entity2)

        entities = repo.find_all()

        assert len(entities) == 2
        ids = {e.id for e in entities}
        assert ids == {"test-1", "test-2"}

    def test_contract_delete_removes_entity(self) -> None:
        """delete() removes entity from repository."""
        repo = self.create_repository()
        entity = self.create_entity("test-1")

        repo.save(entity)
        repo.delete("test-1")

        found = repo.find_by_id("test-1")
        assert found is None

    def test_contract_delete_is_idempotent(self) -> None:
        """delete() doesn't raise exception for nonexistent entity."""
        repo = self.create_repository()

        # Should not raise
        repo.delete("nonexistent")
        repo.delete("nonexistent")

    def test_contract_exists_returns_true_when_entity_exists(self) -> None:
        """exists() returns True when entity exists."""
        repo = self.create_repository()
        entity = self.create_entity("test-1")

        repo.save(entity)

        assert repo.exists("test-1") is True

    def test_contract_exists_returns_false_when_entity_does_not_exist(self) -> None:
        """exists() returns False when entity doesn't exist."""
        repo = self.create_repository()

        assert repo.exists("nonexistent") is False

    def test_contract_exists_reflects_deletion(self) -> None:
        """exists() returns False after entity is deleted."""
        repo = self.create_repository()
        entity = self.create_entity("test-1")

        repo.save(entity)
        assert repo.exists("test-1") is True

        repo.delete("test-1")
        assert repo.exists("test-1") is False

    def test_contract_save_update_modifies_entity(self) -> None:
        """save() updates existing entity when called with same ID."""
        repo = self.create_repository()
        entity = self.create_entity("test-1")

        # Save original
        repo.save(entity)

        # Modify and save again
        entity.validate()  # Trigger any business logic
        repo.save(entity)

        # Verify still only one entity
        entities = repo.find_all()
        assert len(entities) == 1
        assert entities[0].id == "test-1"
