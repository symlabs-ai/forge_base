# ADR-002: Hexagonal Architecture (Ports & Adapters)

## Status

**Accepted** (2025-11-03)

## Context

Complementing Clean Architecture ([ADR-001](001-clean-architecture-choice.md)), we needed a clear pattern to define **how** the application communicates with the external world:

- Databases (persistence)
- External APIs (HTTP, gRPC)
- User interfaces (CLI, Web)
- Messaging systems
- LLMs and AI services

The challenge was to create a pattern that:
- Isolated application logic from implementation details
- Allowed swapping implementations without modifying the core
- Facilitated testing with mocks/fakes
- Kept the domain "pure" and independent
- Made integration points explicit

### Forces at Play

**Needs:**
- Multiple adapters for the same port (e.g., JSON, SQL, MongoDB for persistence)
- Tests without real dependencies (fakes, mocks)
- Independent adapter evolution
- Clarity about integration boundaries

**Risks:**
- Proliferation of unnecessary interfaces
- Overhead of creating ports for everything
- Confusion between driving and driven ports

## Decision

**We adopted Hexagonal Architecture (Ports & Adapters) as the integration pattern.**

### Fundamental Concepts

#### 1. Ports (Interfaces/Contracts)

**Ports are abstract contracts** defined by the application that specify **what** needs to be done, without worrying about **how**.

**Types of Ports:**

**Driving Ports (Primary)** — "Who uses the application"
- Interfaces that trigger the application (input)
- Examples: UseCases, Command Handlers
- Defined by the application layer
- Implemented by external adapters

**Driven Ports (Secondary)** — "What the application uses"
- Interfaces that the application calls (output)
- Examples: RepositoryPort, LoggerPort, NotificationPort
- Defined by the application layer
- Implemented by the infrastructure layer

#### 2. Adapters (Concrete Implementations)

**Adapters are specific implementations** of ports, translating between the domain and external technologies.

**Driving Adapters (Primary):**
```python
# CLIAdapter: Interprets CLI commands → calls UseCases
# HTTPAdapter: Receives HTTP requests → calls UseCases
# AIAdapter: Processes LLM instructions → calls UseCases
```

**Driven Adapters (Secondary):**
```python
# JSONRepository: Implements RepositoryPort → saves to JSON
# SQLRepository: Implements RepositoryPort → saves to SQL
# StdoutLogger: Implements LoggerPort → logs to stdout
```

### ForgeBase Hexagonal Architecture

```
                    ┌─────────────────┐
     CLI ────────► │                 │
                    │   UseCaseBase   │ ◄────── HTTP
     AI  ────────► │  (Driving Port) │
                    │                 │
                    └────────┬────────┘
                             │
                             │ calls
                             ▼
                    ┌─────────────────┐
                    │                 │
                    │  Domain Logic   │
                    │                 │
                    └────────┬────────┘
                             │
                             │ uses
                             ▼
        ┌───────────────────────────────────┐
        │      Driven Ports                 │
        │  (RepositoryPort, LoggerPort)     │
        └───────────┬───────────────────────┘
                    │
        ┌───────────┼───────────┐
        │           │           │
        ▼           ▼           ▼
    [JSON]      [SQL]      [Stdout]
   Adapter     Adapter     Adapter
```

### Implementation in ForgeBase

#### Driving Ports (Primary)

```python
# src/forge_base/application/usecase_base.py
class UseCaseBase(ABC):
    """
    Driving Port — entry point to the application.
    Adapters call execute() to trigger logic.
    """
    @abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        pass
```

**Adapters that implement it:**
- `CLIAdapter` — translates CLI commands → `execute()`
- `HTTPAdapter` — translates HTTP requests → `execute()`

#### Driven Ports (Secondary)

```python
# src/forge_base/application/port_base.py
class PortBase(ABC):
    """Base for all driven ports."""
    @abstractmethod
    def info(self) -> dict:
        pass

# src/forge_base/infrastructure/repository/repository_base.py
class RepositoryBase(PortBase, Generic[T]):
    """
    Driven Port — persistence.
    UseCases depend on this interface, not on implementations.
    """
    @abstractmethod
    def save(self, entity: T) -> None:
        pass

    @abstractmethod
    def find_by_id(self, id: str) -> Optional[T]:
        pass

# src/forge_base/infrastructure/logging/logger_port.py
class LoggerPort(PortBase):
    """
    Driven Port — logging.
    UseCases log through this interface.
    """
    @abstractmethod
    def info(self, message: str, **context) -> None:
        pass
```

**Adapters that implement them:**
- `JSONRepository(RepositoryBase)` — saves to JSON
- `SQLRepository(RepositoryBase)` — saves to SQL
- `StdoutLogger(LoggerPort)` — logs to stdout
- `FileLogger(LoggerPort)` — logs to file

### Implementation Rules

1. **Ports are defined by the Application**, not by Adapters
2. **Adapters are never imported directly by UseCases**
3. **Dependency Injection injects concrete adapters** ([ADR-005](005-dependency-injection.md))
4. **A UseCase depends on Ports, never on Adapters**
5. **Multiple Adapters can implement the same Port**

### Complete Example

```python
# Application Layer — Defines the Port
class UserRepositoryPort(ABC):
    @abstractmethod
    def save(self, user: User) -> None:
        pass

# Use Case — Depends on the Port
class CreateUserUseCase(UseCaseBase):
    def __init__(self, user_repository: UserRepositoryPort):
        self.user_repository = user_repository  # Port, not adapter

    def execute(self, input_dto: CreateUserInput) -> CreateUserOutput:
        user = User(name=input_dto.name, email=input_dto.email)
        self.user_repository.save(user)  # Calls the port
        return CreateUserOutput(user_id=user.id)

# Infrastructure — Implements the Port
class JSONUserRepository(UserRepositoryPort):
    def save(self, user: User) -> None:
        # JSON-specific implementation
        pass

class SQLUserRepository(UserRepositoryPort):
    def save(self, user: User) -> None:
        # SQL-specific implementation
        pass

# Adapter — Driving (CLI)
class CLIAdapter:
    def run_command(self, command: str):
        # Parse command
        usecase = CreateUserUseCase(
            user_repository=injected_repository  # DI injects adapter
        )
        usecase.execute(input_dto)
```

## Consequences

### Positive

✅ **Maximum Testability**
```python
# Tests use FakeRepository, not real SQL
def test_create_user():
    fake_repo = FakeRepository()
    usecase = CreateUserUseCase(user_repository=fake_repo)
    usecase.execute(CreateUserInput(name="Test"))
    assert fake_repo.count() == 1
```

✅ **Implementation Swap Without Core Changes**
```python
# Switch from JSON to SQL — zero changes in the UseCase
# config.yaml
repository: sql  # was "json" before
```

✅ **Multiple Implementations of the Same Port**
```python
# Same port, multiple adapters
- JSONRepository(RepositoryPort)
- SQLRepository(RepositoryPort)
- MongoRepository(RepositoryPort)
- InMemoryRepository(RepositoryPort)
```

✅ **Clarity About Boundaries**
- Easy to see "what comes in" (driving ports)
- Easy to see "what goes out" (driven ports)
- Explicit boundaries in code

✅ **Independent Evolution**
- Adapter can evolve without affecting the application
- New adapter does not require core changes
- Deprecate adapter without breaking changes

### Negative

⚠️ **Abstraction Overhead**
- One port for each external dependency
- "Plumbing" code (DI, wiring)
- More files to navigate

⚠️ **Initial Confusion**
- Difference between port and adapter is not obvious
- Temptation to "skip" the port and use the adapter directly
- Learning curve

⚠️ **Over-Engineering in Simple Cases**
- For stable dependencies (e.g., Python stdlib), a port can be overhead
- Not everything needs an abstraction

### Mitigations

1. **Clear Naming Convention**
   - Ports: `*Port` (e.g., `RepositoryPort`, `LoggerPort`)
   - Adapters: `*Adapter` (e.g., `CLIAdapter`, `HTTPAdapter`)
   - Implementations: `*Repository`, `*Logger` (e.g., `JSONRepository`)

2. **Documentation with Examples**
   - Complete flow example showing port + adapter
   - Cookbook with common recipes
   - ADRs explaining "why"

3. **Tooling**
   - Automatic scaffold of port + adapter
   - Linting to validate boundaries
   - Code generators

4. **Pragmatism Rule**
   - "If the dependency is stable and controlled by us, a port can be optional"
   - "If the dependency is external or can change, a port is mandatory"

## Alternatives Considered

### 1. Direct Coupling (without Ports)

```python
# UseCase imports adapter directly
from infrastructure.json_repository import JSONRepository

class CreateUserUseCase:
    def __init__(self):
        self.repo = JSONRepository()  # Direct coupling
```

**Rejected because:**
- Impossible to swap implementation without modifying UseCase
- Tests require real JSON (slow, fragile)
- Violation of Clean Architecture
- Domain coupled to infrastructure

### 2. Service Locator Pattern

```python
# UseCase requests dependency from a global locator
class CreateUserUseCase:
    def execute(self, input_dto):
        repo = ServiceLocator.get('repository')  # Global
```

**Rejected because:**
- Hidden dependencies (not explicit in signature)
- Complicates tests (global state)
- Implicit coupling
- Complicates dependency tracing

### 3. Concrete Dependencies Everywhere

```python
# Each UseCase creates its own dependencies
class CreateUserUseCase:
    def execute(self, input_dto):
        repo = JSONRepository(path="/data/users.json")  # Hardcoded
```

**Rejected because:**
- Zero flexibility
- Tests impossible without real filesystem
- Hardcoded configuration
- Violation of Single Responsibility

### 4. Ports Only for "Big Things"

**Rejected because:**
- Architectural inconsistency
- Thin line between "big" and "small"
- Tends to degrade over time
- Better to have a clear rule: "every external dependency = port"

## References

- **Hexagonal Architecture** (Ports & Adapters) by Alistair Cockburn
- **Clean Architecture** by Robert C. Martin (chapter on boundaries)
- **Growing Object-Oriented Software, Guided by Tests** by Freeman & Pryce
- ForgeBase complete_flow.py — Practical example of ports & adapters

## Related ADRs

- [ADR-001: Clean Architecture Choice](001-clean-architecture-choice.md)
- [ADR-005: Dependency Injection](005-dependency-injection.md)

---

**Author:** ForgeBase Development Team
**Date:** 2025-11-03
**Version:** 1.0
