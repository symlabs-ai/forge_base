# ForgeBase Examples

This directory contains complete examples demonstrating the ForgeBase cognitive architecture in action.

## Quick Start

Run the complete flow demonstration:

```bash
# From the forgebase root directory
python examples/complete_flow.py
```

This will run through all layers of the architecture and show how they work together.

## What This Example Demonstrates

### 1. Domain Layer (Entities & Value Objects)

**Files:**
- `user_management/domain/user.py` - User Entity with business rules
- `user_management/domain/email.py` - Email ValueObject with validation

**Concepts:**
- Entities have identity and lifecycle
- ValueObjects are immutable and compared by value
- Business rules are enforced in the domain
- Validation happens at domain boundaries

**Example:**
```python
from user_management.domain import User, Email

# Create validated email
email = Email(address="user@example.com")

# Create user entity
user = User(name="John Doe", email=email)
user.validate()

# Business rule: cannot reactivate deactivated user
user.deactivate()
# user.activate()  # Raises BusinessRuleViolation
```

### 2. Application Layer (UseCases, Ports, DTOs)

**Files:**
- `user_management/application/create_user_usecase.py` - UseCase orchestration
- `user_management/application/ports.py` - Repository Port (interface)

**Concepts:**
- UseCases orchestrate business logic
- Ports define contracts for external systems
- DTOs transfer data across boundaries
- Application layer is independent of infrastructure

**Example:**
```python
from user_management.application import CreateUserUseCase, CreateUserInput
from user_management.infrastructure import InMemoryUserRepository

# Setup dependencies
repository = InMemoryUserRepository()
usecase = CreateUserUseCase(user_repository=repository)

# Execute
input_dto = CreateUserInput(name="Alice", email="alice@example.com")
output = usecase.execute(input_dto)

print(f"Created user: {output.user_id}")
```

### 3. Infrastructure Layer (Concrete Implementations)

**Files:**
- `user_management/infrastructure/user_repository.py` - Repository implementation

**Concepts:**
- Infrastructure provides concrete implementations
- Adapters implement Ports
- Can swap implementations without changing application code
- In-memory, JSON, SQL - all implement the same port

**Example:**
```python
from user_management.infrastructure import InMemoryUserRepository

# In-memory (for testing/examples)
repository = InMemoryUserRepository()

# In production, swap with:
# repository = SQLUserRepository(connection_string)
# No application code changes needed!
```

### 4. Observability (Metrics, Logging, Tracing)

**Integrated throughout:**
- Structured logging with context
- Health checks
- System introspection
- Metrics collection (ready for instrumentation)

**Example:**
```python
from forgebase.core_init import ForgeBaseCore

core = ForgeBaseCore()
core.bootstrap()

# Register usecase
core.register_usecase('create_user', usecase)

# Execute with full observability
output = usecase.execute(input_dto)

# Health check
health = core.health_check()
print(f"System healthy: {health['healthy']}")

core.shutdown()
```

## Architecture Patterns Demonstrated

### Clean Architecture

```
┌─────────────────────────────────────┐
│         User Interface              │
│       (CLI, HTTP, AI)               │
│         [Adapters]                  │
├─────────────────────────────────────┤
│       Application Layer             │
│     (UseCases, DTOs, Ports)         │
├─────────────────────────────────────┤
│        Domain Layer                 │
│   (Entities, Value Objects)         │
│      [Business Rules]               │
└─────────────────────────────────────┘
        ↓ depends on ↓
     Infrastructure
   (Repository, Logging)
```

**Dependency Rule**: Inner layers never depend on outer layers.

### Hexagonal Architecture (Ports & Adapters)

```
         ┌──────────────┐
         │   Domain     │
         │   (Core)     │
         └──────┬───────┘
                │
         ┌──────▼───────┐
         │  Application │
         │   (Ports)    │
         └──┬────────┬──┘
            │        │
     ┌──────▼──┐ ┌──▼──────┐
     │ Adapter │ │ Adapter │
     │  (CLI)  │ │ (HTTP)  │
     └─────────┘ └─────────┘
```

**Ports**: Interfaces defined by application
**Adapters**: Concrete implementations

## File Structure

```
examples/
├── README.md                    # This file
├── complete_flow.py            # Main demonstration
└── user_management/            # Example domain
    ├── domain/                 # Domain Layer
    │   ├── user.py            # User Entity
    │   └── email.py           # Email ValueObject
    ├── application/            # Application Layer
    │   ├── ports.py           # Repository Port
    │   └── create_user_usecase.py  # CreateUser UseCase
    └── infrastructure/         # Infrastructure Layer
        └── user_repository.py  # In-Memory Repository
```

## Key Takeaways

1. **Layer Separation**: Each layer has clear responsibilities
2. **Dependency Inversion**: Inner layers define interfaces, outer implement them
3. **Testability**: Easy to test with fakes/mocks
4. **Maintainability**: Changes are isolated to specific layers
5. **Observability**: Built-in metrics, logging, health checks
6. **Cognitive Coherence**: Patterns are consistent throughout

## Next Steps

1. **Explore the Code**: Read through each file to understand implementation
2. **Run Tests**: See how the testing infrastructure works
3. **Create Your Own**: Try implementing a new UseCase
4. **Experiment**: Swap the in-memory repository for a JSON one
5. **Extend**: Add more features to the user management example

## Philosophical Notes

This framework embodies three core principles:

1. **Reflexividade** (Reflexivity): The system understands itself
   - Health checks, introspection, self-documentation

2. **Autonomia** (Autonomy): Modules are independent
   - Clear boundaries, dependency injection, port/adapter pattern

3. **Coerência Cognitiva** (Cognitive Coherence): Consistent patterns
   - Same patterns across layers, predictable structure, clear conventions

## Further Reading

- `docs/BACKLOG.md` - Full development roadmap
- `src/forgebase/` - Core framework implementation
- `tests/` - Test examples and patterns

---

**"Forjar é transformar pensamento em estrutura."**
