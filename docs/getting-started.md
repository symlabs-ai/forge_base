# Getting Started with ForgeBase

> "Forjar é transformar pensamento em estrutura."

ForgeBase é um framework cognitivo para desenvolvimento de aplicações Python com Clean Architecture, observabilidade nativa e validação de coerência entre intenção e execução.

Este guia vai levá-lo do zero até sua primeira aplicação funcional em ~30 minutos.

---

## 📋 Pré-requisitos

- **Python 3.11+** instalado
- **pip** para gerenciar pacotes
- **Git** (opcional, para clonar exemplos)
- Editor de código (VS Code, PyCharm, etc.)

---

## 🚀 Instalação

### Opção 1: Instalação via pip (quando publicado)

```bash
pip install forgebase
```

### Opção 2: Instalação a partir do código-fonte

```bash
# Clone o repositório
git clone https://github.com/symlabs-ai/forgebase.git
cd forgebase

# Instale em modo de desenvolvimento
pip install -e .

# Ou instale dependências manualmente
pip install pyyaml  # Para configuração
```

### Verificar Instalação

```bash
python -c "import forgebase; print(forgebase.__version__)"
# Output: 1.0.0
```

---

## 🎯 Seu Primeiro UseCase

Vamos criar uma aplicação simples de gerenciamento de tarefas (TODO list) usando ForgeBase.

### Estrutura do Projeto

```bash
mkdir my-forge-app
cd my-forge-app

# Criar estrutura
mkdir -p src/domain
mkdir -p src/application
mkdir -p src/infrastructure
mkdir -p tests

touch src/__init__.py
touch src/domain/__init__.py
touch src/application/__init__.py
touch src/infrastructure/__init__.py
```

### 1. Domain Layer: Entidade Task

Primeiro, criamos a entidade de domínio que representa uma tarefa.

```python
# src/domain/task.py
"""
Domain entity: Task.

Represents a TODO task with title, description and completion status.
"""

from datetime import datetime
from forgebase.domain import EntityBase, ValidationError


class Task(EntityBase):
    """
    Task entity.

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
            raise ValidationError("Task title too long (max 200 characters)")

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

### 2. Application Layer: DTOs e Port

```python
# src/application/task_dtos.py
"""DTOs for Task management."""

from forgebase.application import DTOBase


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
    """Output from creating a task."""

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
"""Repository port for Task entities."""

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
        """Find task by ID."""
        pass

    @abstractmethod
    def find_all(self) -> list[Task]:
        """Find all tasks."""
        pass

    @abstractmethod
    def delete(self, task_id: str) -> None:
        """Delete a task."""
        pass

    @abstractmethod
    def exists(self, task_id: str) -> bool:
        """Check if task exists."""
        pass
```

### 3. Application Layer: UseCase

```python
# src/application/create_task_usecase.py
"""UseCase for creating a new task."""

from forgebase.application import UseCaseBase
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
            description="Follow the getting started guide"
        ))
        print(f"Task created: {output.task_id}")
    """

    def __init__(self, task_repository: TaskRepositoryPort):
        self.task_repository = task_repository

    def execute(self, input_dto: CreateTaskInput) -> CreateTaskOutput:
        """
        Execute task creation.

        :param input_dto: Task data
        :type input_dto: CreateTaskInput
        :return: Created task info
        :rtype: CreateTaskOutput
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
        """Return number of tasks."""
        return len(self._storage)
```

### 5. Executando Seu UseCase

```python
# main.py
"""Main application entry point."""

from src.application.create_task_usecase import CreateTaskUseCase
from src.application.task_dtos import CreateTaskInput
from src.infrastructure.in_memory_task_repository import InMemoryTaskRepository


def main():
    # Setup dependencies
    repository = InMemoryTaskRepository()

    # Create use case
    usecase = CreateTaskUseCase(task_repository=repository)

    # Execute
    output = usecase.execute(CreateTaskInput(
        title="Learn ForgeBase",
        description="Complete the getting started guide"
    ))

    # Display result
    print(f"✓ Task created!")
    print(f"  ID: {output.task_id}")
    print(f"  Title: {output.title}")
    print(f"  Created: {output.created_at}")


if __name__ == "__main__":
    main()
```

Executar:

```bash
python main.py
```

Output:

```
✓ Task created!
  ID: 550e8400-e29b-41d4-a716-446655440000
  Title: Learn ForgeBase
  Created: 2025-11-03T10:30:00
```

---

## 🧪 Testando Seu UseCase

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
        """Test that task is created successfully."""
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
        """Test that empty title is rejected."""
        with self.assertRaises(ValueError):
            self.usecase.execute(CreateTaskInput(title=""))


if __name__ == "__main__":
    unittest.main()
```

Executar testes:

```bash
python -m pytest tests/
```

---

## 📊 Adicionando Observabilidade

ForgeBase tem observabilidade nativa. Vamos adicionar logging e métricas:

```python
# main_with_observability.py
"""Main application with observability."""

from forgebase.observability import LogService, TrackMetrics
from src.application.create_task_usecase import CreateTaskUseCase
from src.application.task_dtos import CreateTaskInput
from src.infrastructure.in_memory_task_repository import InMemoryTaskRepository


def main():
    # Setup observability
    logger = LogService(name="my-app")
    metrics = TrackMetrics()

    # Setup dependencies
    repository = InMemoryTaskRepository()

    # Create use case
    usecase = CreateTaskUseCase(task_repository=repository)

    # Execute with logging
    logger.info("Creating task", title="Learn ForgeBase")

    with metrics.measure("create_task"):
        output = usecase.execute(CreateTaskInput(
            title="Learn ForgeBase",
            description="Complete the getting started guide"
        ))

    logger.info("Task created", task_id=output.task_id, title=output.title)

    # Report metrics
    print("\nMetrics:")
    report = metrics.report()
    for metric_name, metric_data in report.items():
        print(f"  {metric_name}: {metric_data}")


if __name__ == "__main__":
    main()
```

Output:

```
[2025-11-03 10:30:00] INFO: Creating task (title=Learn ForgeBase)
[2025-11-03 10:30:00] INFO: Task created (task_id=550e8400..., title=Learn ForgeBase)

Metrics:
  create_task.duration: 2.5ms
  create_task.count: 1
```

---

## 🔄 Próximos Passos

Parabéns! Você criou sua primeira aplicação ForgeBase. Agora você pode:

### 1. Adicionar Mais UseCases

```python
# UpdateTaskUseCase, DeleteTaskUseCase, ListTasksUseCase, etc.
```

### 2. Trocar de Repository

```python
# Em vez de InMemoryTaskRepository, use:
from forgebase.infrastructure.repository import JSONRepository

repository = JSONRepository(
    file_path="data/tasks.json",
    entity_type=Task
)
```

### 3. Adicionar Adapters

```python
# CLI Adapter
from forgebase.adapters.cli import CLIAdapter

cli = CLIAdapter()
cli.register_command("create-task", CreateTaskUseCase)

# HTTP Adapter
from forgebase.adapters.http import HTTPAdapter

http = HTTPAdapter()
http.register_endpoint("/tasks", method="POST", usecase=CreateTaskUseCase)
```

### 4. Integrar com ForgeProcess

```python
# Sincronização YAML ↔ Code
from forgebase.integration import YAMLSync

sync = YAMLSync()
spec = sync.parse_yaml("specs/create_task.yaml")
code = sync.generate_code(spec)
```

### 5. Validar Coerência Cognitiva

```python
# Intent tracking
from forgebase.integration import IntentTracker

tracker = IntentTracker()
intent_id = tracker.capture_intent(
    description="Create a task for learning ForgeBase",
    expected_outcome="Task created successfully"
)

output = usecase.execute(input_dto)

tracker.record_execution(
    intent_id=intent_id,
    actual_outcome=f"Task {output.task_id} created",
    success=True
)

report = tracker.validate_coherence(intent_id)
print(f"Coherence: {report.coherence_level.value}")
```

---

## 📚 Recursos Adicionais

### Documentação

- **[Example Cookbook](cookbook.md)** — Receitas para casos comuns
- **[Testing Guide](testing-guide.md)** — Como escrever testes cognitivos
- **[API Reference](api/)** — Referência completa da API
- **[ADRs](adr/)** — Architecture Decision Records

### Exemplos

Explore exemplos completos em `examples/`:

```bash
cd examples

# Complete flow example (todos os layers)
python complete_flow.py

# Integration demo (YAML sync + Intent tracking)
python integration_demo.py

# User management example
cd user_management
python ../../main.py
```

### Conceitos-Chave

**Clean Architecture:**
- Domain não depende de nada
- Application orquestra lógica
- Infrastructure implementa detalhes
- Adapters conectam com mundo externo

**Hexagonal Architecture (Ports & Adapters):**
- Ports = Contratos (interfaces)
- Adapters = Implementações
- Dependency Injection para wiring

**Observabilidade First:**
- Logging estruturado
- Métricas automáticas
- Distributed tracing
- Intent tracking

**Cognitive Testing:**
- Validar intenção, não apenas comportamento
- ForgeTestCase com assertions cognitivas
- Fakes para testes rápidos

---

## ❓ Problemas Comuns

### Import Error: "No module named 'forgebase'"

```bash
# Certifique-se de instalar ForgeBase
pip install -e .

# Ou adicione ao PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
```

### ValidationError: "Task title cannot be empty"

Isso é esperado! Entidades de domínio validam suas invariantes. Sempre passe dados válidos:

```python
# ❌ Vai falhar
task = Task(title="")

# ✅ Correto
task = Task(title="Valid title")
```

### Type Hints: "Type not found"

Certifique-se de usar Python 3.11+:

```bash
python --version
# Python 3.11.0 or higher
```

---

## 💡 Dicas

1. **Comece Simples**: Domain puro, um UseCase, um teste
2. **Adicione Gradualmente**: Observabilidade, adapters, integração
3. **Siga os Exemplos**: `examples/` tem implementações completas
4. **Leia os ADRs**: Entenda as decisões arquiteturais
5. **Use Fakes nos Testes**: InMemoryRepository, FakeLogger, etc.

---

## 🤝 Contribuindo

Encontrou um bug? Tem uma sugestão? Veja **[CONTRIBUTING.md](../CONTRIBUTING.md)**.

---

## 📖 Próximas Leituras

- **[Example Cookbook](cookbook.md)** — Receitas práticas
- **[ADR-001: Clean Architecture](adr/001-clean-architecture-choice.md)** — Por que Clean Architecture?
- **[Testing Guide](testing-guide.md)** — Testes cognitivos
- **[Module Extension Guide](extending-forgebase.md)** — Como estender ForgeBase

---

**Feliz Forjamento! 🔨**

*"Cada linha de código carrega intenção, medição e capacidade de auto-explicação."*
