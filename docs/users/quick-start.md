# Quick Start with ForgeBase

> "To forge is to transform thought into structure."

This guide will take you from zero to your first working application in ~30 minutes.

---

## Prerequisites

- **Python 3.11+** installed
- **pip** for package management
- **Git** for cloning the repository
- Code editor (VS Code, PyCharm, etc.)

---

## Installation

### Option 1: Install via pip (production)

```bash
# Install latest version from main
pip install git+https://github.com/symlabs-ai/forge_base.git

# Verify installation
python -c "from forge_base.dev.api import QualityChecker; print('ForgeBase installed!')"
```

### Option 2: Install for development

```bash
# Clone and install in editable mode
git clone https://github.com/symlabs-ai/forge_base.git
cd forge_base

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# or: .venv\Scripts\activate  # Windows

# Install with development dependencies
pip install -e ".[dev]"
```

### Option 3: With optional dependencies

```bash
# With SQL support (SQLAlchemy)
pip install "forge_base[sql] @ git+https://github.com/symlabs-ai/forge_base.git"

# With all dependencies
pip install "forge_base[all] @ git+https://github.com/symlabs-ai/forge_base.git"
```

---

## Your First UseCase

Let's create a simple task management application using ForgeBase.

### Project Structure

```bash
mkdir my-forge-app
cd my-forge-app

# Create directory structure
mkdir -p src/domain
mkdir -p src/application
mkdir -p src/infrastructure
mkdir -p tests

touch src/__init__.py
touch src/domain/__init__.py
touch src/application/__init__.py
touch src/infrastructure/__init__.py
```

### 1. Domain Layer: Task Entity

```python
# src/domain/task.py
"""Domain entity: Task."""

from datetime import datetime
from forge_base.domain import EntityBase, ValidationError


class Task(EntityBase):
    """
    Task Entity.

    A task has a title, optional description, and completion status.
    Tasks are created as incomplete by default.
    """

    def __init__(
        self,
        title: str,
        description: str = "",
        id: str | None = None,
        completed: bool = False,
        created_at: datetime | None = None
    ):
        super().__init__(id=id)
        self.title = title
        self.description = description
        self.completed = completed
        self.created_at = created_at or datetime.now()
        self.validate()

    def validate(self) -> None:
        """Validate task invariants."""
        if not self.title or not self.title.strip():
            raise ValidationError("Task title cannot be empty")

        if len(self.title) > 200:
            raise ValidationError("Title too long (maximum 200 characters)")

    def complete(self) -> None:
        """Mark task as completed."""
        self.completed = True

    def uncomplete(self) -> None:
        """Mark task as incomplete."""
        self.completed = False

    def __str__(self) -> str:
        status = "✓" if self.completed else "○"
        return f"{status} {self.title}"
```

### 2. Application Layer: DTOs and Port

```python
# src/application/task_dtos.py
"""DTOs for Task management."""

from forge_base.application import DTOBase


class CreateTaskInput(DTOBase):
    """Input for creating a task."""

    def __init__(self, title: str, description: str = ""):
        self.title = title
        self.description = description

    def validate(self) -> None:
        if not self.title:
            raise ValueError("Title is required")

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "description": self.description
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'CreateTaskInput':
        return cls(
            title=data.get("title", ""),
            description=data.get("description", "")
        )


class CreateTaskOutput(DTOBase):
    """Output from task creation."""

    def __init__(self, task_id: str, title: str, created_at: str):
        self.task_id = task_id
        self.title = title
        self.created_at = created_at

    def validate(self) -> None:
        pass

    def to_dict(self) -> dict:
        return {
            "task_id": self.task_id,
            "title": self.title,
            "created_at": self.created_at
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'CreateTaskOutput':
        return cls(
            task_id=data["task_id"],
            title=data["title"],
            created_at=data["created_at"]
        )
```

```python
# src/application/task_repository_port.py
"""Repository port for the Task entity."""

from abc import ABC, abstractmethod
from src.domain.task import Task


class TaskRepositoryPort(ABC):
    """
    Port for Task persistence.

    Defines the contract for storing and retrieving tasks,
    without specifying implementation details.
    """

    @abstractmethod
    def save(self, task: Task) -> None:
        """Save a task."""
        pass

    @abstractmethod
    def find_by_id(self, task_id: str) -> Task | None:
        """Find a task by ID."""
        pass

    @abstractmethod
    def find_all(self) -> list[Task]:
        """Find all tasks."""
        pass

    @abstractmethod
    def delete(self, task_id: str) -> None:
        """Remove a task."""
        pass

    @abstractmethod
    def exists(self, task_id: str) -> bool:
        """Check if a task exists."""
        pass
```

### 3. Application Layer: UseCase

```python
# src/application/create_task_usecase.py
"""UseCase for creating a new task."""

from forge_base.application import UseCaseBase
from src.domain.task import Task
from src.application.task_dtos import CreateTaskInput, CreateTaskOutput
from src.application.task_repository_port import TaskRepositoryPort


class CreateTaskUseCase(UseCaseBase):
    """
    Create a new task.

    Orchestrates the creation of a task entity and its persistence.

    Example::

        usecase = CreateTaskUseCase(task_repository=repository)
        output = usecase.execute(CreateTaskInput(
            title="Learn ForgeBase",
            description="Follow the quick start guide"
        ))
        print(f"Task created: {output.task_id}")
    """

    def __init__(self, task_repository: TaskRepositoryPort):
        self.task_repository = task_repository

    def execute(self, input_dto: CreateTaskInput) -> CreateTaskOutput:
        """
        Execute task creation.

        :param input_dto: Task data
        :return: Created task information
        """
        # Validate input
        input_dto.validate()

        # Create domain entity
        task = Task(
            title=input_dto.title,
            description=input_dto.description
        )

        # Validate domain rules
        task.validate()

        # Persist
        self.task_repository.save(task)

        # Return output
        return CreateTaskOutput(
            task_id=task.id,
            title=task.title,
            created_at=task.created_at.isoformat()
        )
```

### 4. Infrastructure Layer: In-Memory Repository

```python
# src/infrastructure/in_memory_task_repository.py
"""In-memory implementation of TaskRepositoryPort."""

from src.application.task_repository_port import TaskRepositoryPort
from src.domain.task import Task


class InMemoryTaskRepository(TaskRepositoryPort):
    """
    In-memory task repository.

    Stores tasks in a dictionary. Useful for testing and prototyping.
    """

    def __init__(self):
        self._storage: dict[str, Task] = {}

    def save(self, task: Task) -> None:
        task.validate()
        self._storage[task.id] = task

    def find_by_id(self, task_id: str) -> Task | None:
        return self._storage.get(task_id)

    def find_all(self) -> list[Task]:
        return list(self._storage.values())

    def delete(self, task_id: str) -> None:
        if task_id in self._storage:
            del self._storage[task_id]

    def exists(self, task_id: str) -> bool:
        return task_id in self._storage

    def count(self) -> int:
        """Return the number of tasks."""
        return len(self._storage)
```

### 5. Running Your UseCase

```python
# main.py
"""Application entry point."""

from src.application.create_task_usecase import CreateTaskUseCase
from src.application.task_dtos import CreateTaskInput
from src.infrastructure.in_memory_task_repository import InMemoryTaskRepository


def main():
    # Set up dependencies
    repository = InMemoryTaskRepository()

    # Create use case
    usecase = CreateTaskUseCase(task_repository=repository)

    # Execute
    output = usecase.execute(CreateTaskInput(
        title="Learn ForgeBase",
        description="Complete the quick start guide"
    ))

    # Display result
    print(f"Task created!")
    print(f"  ID: {output.task_id}")
    print(f"  Title: {output.title}")
    print(f"  Created at: {output.created_at}")


if __name__ == "__main__":
    main()
```

Run it:

```bash
python main.py
```

Expected output:

```
Task created!
  ID: 550e8400-e29b-41d4-a716-446655440000
  Title: Learn ForgeBase
  Created at: 2025-11-03T10:30:00
```

---

## Testing Your UseCase

```python
# tests/test_create_task_usecase.py
"""Tests for CreateTaskUseCase."""

import unittest
from src.application.create_task_usecase import CreateTaskUseCase
from src.application.task_dtos import CreateTaskInput
from src.infrastructure.in_memory_task_repository import InMemoryTaskRepository


class TestCreateTaskUseCase(unittest.TestCase):
    def setUp(self):
        self.repository = InMemoryTaskRepository()
        self.usecase = CreateTaskUseCase(task_repository=self.repository)

    def test_creates_task(self):
        """Test that a task is created successfully."""
        # Execute
        output = self.usecase.execute(CreateTaskInput(
            title="Test task",
            description="Test description"
        ))

        # Assertions
        self.assertIsNotNone(output.task_id)
        self.assertEqual(output.title, "Test task")

        # Verify persistence
        self.assertEqual(self.repository.count(), 1)
        task = self.repository.find_by_id(output.task_id)
        self.assertIsNotNone(task)
        self.assertEqual(task.title, "Test task")

    def test_rejects_empty_title(self):
        """Test that an empty title is rejected."""
        with self.assertRaises(ValueError):
            self.usecase.execute(CreateTaskInput(title=""))


if __name__ == "__main__":
    unittest.main()
```

Run the tests:

```bash
python -m pytest tests/
```

---

## Using the Programmatic APIs

ForgeBase offers APIs for automation:

```python
from forge_base.dev.api import (
    QualityChecker,
    ScaffoldGenerator,
    ComponentDiscovery,
    TestRunner
)

# 1. Check code quality
checker = QualityChecker()
results = checker.run_all()
for tool, result in results.items():
    status = "OK" if result.passed else "ERROR"
    print(f"{tool}: {status}")

# 2. Generate boilerplate
generator = ScaffoldGenerator()
result = generator.create_usecase(
    name="DeleteTask",
    input_type="DeleteTaskInput",
    output_type="DeleteTaskOutput"
)
print(f"Code generated at: {result.file_path}")

# 3. Discover components
discovery = ComponentDiscovery()
components = discovery.scan_project()
print(f"Found: {len(components.entities)} entities")

# 4. Run tests
runner = TestRunner()
results = runner.run_all()
```

---

## Next Steps

1. **Add more UseCases**: UpdateTask, DeleteTask, ListTasks
2. **Swap the repository**: Use `JSONRepository` or `SQLRepository`
3. **Add observability**: Logging and metrics
4. **Read the full documentation**: See [docs/](../README.md)

---

## Common Issues

### Import Error: "No module named 'forge_base'"

```bash
# Install ForgeBase
pip install git+https://github.com/symlabs-ai/forge_base.git

# Or add to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
```

### ValidationError: "Task title cannot be empty"

This is expected! Domain entities validate their invariants. Always pass valid data:

```python
# Will fail
task = Task(title="")

# Correct
task = Task(title="Valid title")
```

### git: command not found

```bash
# Ubuntu/Debian
sudo apt-get install git

# macOS
brew install git
```

---

## Additional Resources

- [Recipes](recipes.md) -- Patterns and practical examples
- [Testing Guide](testing-guide.md) -- How to write cognitive tests
- [ForgeProcess](../reference/forge-process.md) -- Complete cognitive cycle
- [Architecture](../reference/architecture.md) -- Framework structure

---

**Happy Forging!**

*"Every line of code carries intention, measurement, and the ability to self-explain."*
