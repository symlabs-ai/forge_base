# ADR-005: Dependency Injection

## Status

**Accepted** (2025-11-03)

## Context

ForgeBase adopts Clean Architecture ([ADR-001](001-clean-architecture-choice.md)) and Hexagonal Architecture ([ADR-002](002-hexagonal-ports-adapters.md)), which means that:

- **UseCases depend on Ports, not on concrete Adapters**
- **Domain must be completely independent of infrastructure**
- **Adapters can be swapped without modifying the core**

For this to work, we need a mechanism to **inject dependencies** at runtime. The challenge is choosing how to do this in a way that:

- Keeps the architecture clean
- Is testable
- Is configurable
- Does not add unnecessary complexity
- Is explicit (not magical)

### Problem

```python
# ❌ Problem: UseCase creates its own dependencies
class CreateUserUseCase:
    def __init__(self):
        # Direct coupling
        self.repository = JSONRepository("/data/users.json")
        self.logger = StdoutLogger()

    def execute(self, input_dto):
        # Impossible to test without real filesystem
        # Impossible to swap implementation
        ...
```

### Needs

1. **Dependency Inversion**: UseCases depend on abstractions (Ports)
2. **Configurability**: Choose implementations via config
3. **Testability**: Inject fakes in tests
4. **Explicitness**: Dependencies visible in the signature
5. **Lifecycle Management**: Create/destroy dependencies correctly

### Forces at Play

**Needs:**
- Total decoupling between layers
- Fast tests with fakes
- Configuration flexibility
- Component reusability

**Risks:**
- Setup complexity
- "Magic" that complicates debugging
- DI framework overhead
- Learning curve

## Decision

**We adopted Manual Dependency Injection (Constructor Injection) with an Optional DI Container.**

### Principle: Constructor Injection

**All dependencies are injected via constructor:**

```python
# ✅ Solution: Injected dependencies
class CreateUserUseCase(UseCaseBase):
    def __init__(
        self,
        user_repository: UserRepositoryPort,  # Port, not adapter
        logger: LoggerPort,
        metrics: TrackMetrics
    ):
        self.user_repository = user_repository
        self.logger = logger
        self.metrics = metrics

    def execute(self, input_dto: CreateUserInput) -> CreateUserOutput:
        # Uses injected dependencies
        self.logger.info("Creating user", email=input_dto.email)
        ...
```

**Benefits:**
- ✅ **Explicit**: Dependencies visible in the signature
- ✅ **Testable**: Easy to inject fakes
- ✅ **Type-safe**: Clear type hints
- ✅ **Zero magic**: No decorators or metaclasses
- ✅ **IDE-friendly**: Autocomplete works

### Injection Pattern

#### 1. UseCases (Application Layer)

```python
class CreateUserUseCase(UseCaseBase):
    def __init__(
        self,
        user_repository: UserRepositoryPort,  # Required
        logger: Optional[LoggerPort] = None,  # Optional with default
        metrics: Optional[TrackMetrics] = None
    ):
        self.user_repository = user_repository
        self.logger = logger or NoOpLogger()
        self.metrics = metrics or NoOpMetrics()
```

**Conventions:**
- **Required** dependencies without default
- **Optional** dependencies with NoOp default
- Type hints always present
- Descriptive names (not generic like `repo`)

#### 2. Adapters

```python
class JSONUserRepository(UserRepositoryPort):
    def __init__(
        self,
        file_path: str,
        logger: Optional[LoggerPort] = None
    ):
        self.file_path = file_path
        self.logger = logger or NoOpLogger()
```

#### 3. Infrastructure

```python
class SQLRepository(RepositoryBase[T]):
    def __init__(
        self,
        connection_string: str,
        entity_type: Type[T],
        logger: Optional[LoggerPort] = None
    ):
        self.connection_string = connection_string
        self.entity_type = entity_type
        self.logger = logger or NoOpLogger()
```

### DI Container (Optional)

For complex applications, we provide a **simple DI Container**:

```python
# src/forge_base/infrastructure/di_container.py
class DIContainer:
    """
    Simple dependency injection container.

    Registers factories and resolves dependencies automatically.
    """

    def __init__(self):
        self._factories = {}
        self._singletons = {}

    def register(
        self,
        interface: Type,
        factory: Callable,
        singleton: bool = False
    ):
        """Register a factory for an interface."""
        self._factories[interface] = (factory, singleton)

    def resolve(self, interface: Type) -> Any:
        """Resolve an instance of an interface."""
        if interface in self._singletons:
            return self._singletons[interface]

        if interface not in self._factories:
            raise ValueError(f"No factory registered for {interface}")

        factory, singleton = self._factories[interface]
        instance = factory(self)

        if singleton:
            self._singletons[interface] = instance

        return instance
```

**Usage:**

```python
# Setup (application startup)
container = DIContainer()

# Register adapters
container.register(
    LoggerPort,
    lambda c: StdoutLogger(),
    singleton=True
)

container.register(
    UserRepositoryPort,
    lambda c: JSONUserRepository(
        file_path="/data/users.json",
        logger=c.resolve(LoggerPort)
    ),
    singleton=True
)

container.register(
    TrackMetrics,
    lambda c: PrometheusMetrics(endpoint="http://localhost:9090"),
    singleton=True
)

# Register UseCases
container.register(
    CreateUserUseCase,
    lambda c: CreateUserUseCase(
        user_repository=c.resolve(UserRepositoryPort),
        logger=c.resolve(LoggerPort),
        metrics=c.resolve(TrackMetrics)
    )
)

# Resolve UseCase (automatically resolves dependencies)
usecase = container.resolve(CreateUserUseCase)
result = usecase.execute(input_dto)
```

### Configuration-Based DI

Integration with ConfigLoader:

```yaml
# config.yaml
dependencies:
  logger:
    type: stdout
    level: info

  repository:
    type: json
    path: /data/users.json

  metrics:
    type: prometheus
    endpoint: http://localhost:9090

usecases:
  create_user:
    repository: user_repository
    logger: logger
    metrics: metrics
```

```python
# Config loader for DI
class DIConfigLoader:
    def load_from_config(self, config_path: str) -> DIContainer:
        config = load_yaml(config_path)
        container = DIContainer()

        # Register dependencies from config
        for name, dep_config in config['dependencies'].items():
            factory = self._create_factory(dep_config)
            interface = self._get_interface(name)
            container.register(interface, factory, singleton=True)

        return container
```

### Testing with DI

```python
class TestCreateUserUseCase(unittest.TestCase):
    def setUp(self):
        # Manual injection with fakes (no DI container)
        self.fake_repo = FakeRepository()
        self.fake_logger = FakeLogger()
        self.fake_metrics = FakeMetricsCollector()

        self.usecase = CreateUserUseCase(
            user_repository=self.fake_repo,
            logger=self.fake_logger,
            metrics=self.fake_metrics
        )

    def test_creates_user(self):
        result = self.usecase.execute(CreateUserInput(...))

        # Validations
        self.assertEqual(self.fake_repo.count(), 1)
        self.assertTrue(self.fake_logger.was_called('info'))
        self.assertTrue(self.fake_metrics.has_metric('create_user.count'))
```

**No DI container in tests:**
- Simpler setup
- Full control
- No surprises

### Lifecycle Management

```python
class DIContainer:
    def __enter__(self):
        """Context manager for lifecycle."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Cleanup of singletons."""
        for instance in self._singletons.values():
            if hasattr(instance, 'close'):
                instance.close()

# Usage
with DIContainer() as container:
    # Register & resolve
    usecase = container.resolve(CreateUserUseCase)
    usecase.execute(input_dto)
    # Automatic cleanup on exit
```

### core_init.py Integration

```python
# src/forge_base/core_init.py
class ForgeBaseCore:
    def __init__(self, config_path: Optional[str] = None):
        self.config = ConfigLoader.load(config_path)
        self.container = DIContainer()
        self._setup_dependencies()

    def _setup_dependencies(self):
        """Setup DI container from config."""
        # Logger
        logger_config = self.config.get('logger', {})
        self.container.register(
            LoggerPort,
            lambda c: self._create_logger(logger_config),
            singleton=True
        )

        # Metrics
        metrics_config = self.config.get('metrics', {})
        self.container.register(
            TrackMetrics,
            lambda c: self._create_metrics(metrics_config),
            singleton=True
        )

        # Repository
        repo_config = self.config.get('repository', {})
        self.container.register(
            UserRepositoryPort,
            lambda c: self._create_repository(repo_config),
            singleton=True
        )

        # UseCases
        self._register_usecases()

    def get_usecase(self, usecase_class: Type[UseCaseBase]) -> UseCaseBase:
        """Get UseCase with dependencies injected."""
        return self.container.resolve(usecase_class)
```

## Consequences

### Positive

✅ **Maximum Testability**
```python
# Injecting fakes is trivial
usecase = CreateUserUseCase(
    user_repository=FakeRepository(),
    logger=FakeLogger()
)
```

✅ **Configuration Flexibility**
```yaml
# Swap implementations without code changes
repository:
  type: sql  # was "json" before
```

✅ **Explicitness**
```python
# Dependencies visible in the signature
def __init__(self, user_repository: UserRepositoryPort, logger: LoggerPort):
    ...
```

✅ **Type Safety**
- Type hints ensure contracts
- IDE autocomplete works
- Mypy detects errors

✅ **Zero Magic**
- No @inject decorators
- No metaclasses
- Simple debugging

✅ **Reusability**
```python
# Same UseCase, multiple contexts
prod_usecase = CreateUserUseCase(sql_repo, prod_logger)
test_usecase = CreateUserUseCase(fake_repo, fake_logger)
```

### Negative

⚠️ **Wiring Boilerplate**
```python
# Need to wire manually
usecase = CreateUserUseCase(
    user_repository=container.resolve(UserRepositoryPort),
    logger=container.resolve(LoggerPort),
    metrics=container.resolve(TrackMetrics)
)
```

**Mitigation**: DI Container automates wiring

⚠️ **Verbose Initial Setup**
- Many `container.register()` calls
- Config YAML can get extensive

**Mitigation**: Sensible defaults, auto-discovery

⚠️ **Constructor Bloat**
```python
# Too many dependencies = large constructor
def __init__(self, dep1, dep2, dep3, dep4, dep5):
    ...
```

**Mitigation**: If >5 dependencies, refactor the UseCase

### Implemented Mitigations

1. **NoOp Defaults**
   ```python
   def __init__(self, logger: Optional[LoggerPort] = None):
       self.logger = logger or NoOpLogger()
   ```

2. **Simplified Container**
   - Not a complex framework (Guice, Spring)
   - ~200 LOC total
   - Easy to understand and debug

3. **Config-Driven**
   - YAML defines wiring
   - Code only implements
   - Switching without rebuild

4. **Generators**
   ```bash
   forge_base generate usecase CreateUser --with-di
   # Generates UseCase with correct DI
   ```

## Alternatives Considered

### 1. Service Locator

```python
class CreateUserUseCase:
    def execute(self, input_dto):
        repo = ServiceLocator.get(UserRepositoryPort)
        logger = ServiceLocator.get(LoggerPort)
        ...
```

**Rejected because:**
- Hidden dependencies
- Complicates tests
- Global state
- Not type-safe

### 2. Heavy DI Frameworks (Injector, Dependency-Injector)

**Rejected because:**
- Unnecessary overhead
- Too much magic (decorators, metaclasses)
- Learning curve
- ForgeBase aims to be simple

### 3. Function-based DI

```python
def create_user(
    input_dto: CreateUserInput,
    repository: UserRepositoryPort = Depends(get_repository)
):
    ...
```

**Rejected because:**
- Specific to web frameworks (FastAPI)
- Does not apply well to UseCases
- Mixes concerns

### 4. Property Injection

```python
class CreateUserUseCase:
    @inject
    def set_repository(self, repo: UserRepositoryPort):
        self.repository = repo
```

**Rejected because:**
- Less explicit than constructor
- Allows object in invalid state
- More verbose

### 5. Monkey Patching for Tests

```python
# In tests
CreateUserUseCase.repository = FakeRepository()
```

**Rejected because:**
- Global state
- Race conditions
- Not isolated between tests
- Terrible

## Implementation Guidelines

### For UseCase Developers

**Always use constructor injection:**
```python
class MyUseCase(UseCaseBase):
    def __init__(
        self,
        required_port: SomePort,
        optional_port: Optional[OtherPort] = None
    ):
        self.required_port = required_port
        self.optional_port = optional_port or NoOpPort()
```

**Rules:**
1. Required dependencies first
2. Optional dependencies with defaults
3. Type hints always
4. Descriptive names

### For Integration

**Use DI Container for apps:**
```python
# main.py
container = DIContainer()
# ... register dependencies ...
usecase = container.resolve(CreateUserUseCase)
```

**Use manual injection for tests:**
```python
# test_*.py
usecase = CreateUserUseCase(
    repository=FakeRepository(),
    logger=FakeLogger()
)
```

## References

- **Dependency Injection Principles, Practices, and Patterns** by Steven van Deursen & Mark Seemann
- **Clean Architecture** by Robert C. Martin (chapter on DI)
- **Inversion of Control Containers and the Dependency Injection pattern** by Martin Fowler

## Related ADRs

- [ADR-001: Clean Architecture Choice](001-clean-architecture-choice.md)
- [ADR-002: Hexagonal Ports & Adapters](002-hexagonal-ports-adapters.md)

---

**Author:** ForgeBase Development Team
**Date:** 2025-11-03
**Version:** 1.0
