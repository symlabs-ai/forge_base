# ForgeBase Rules -- Complete Developer Guide

> "To forge is to transform thought into structure."

This document consolidates all the rules, practices, and considerations for developing with ForgeBase.

---

## 1. Layered Architecture

### Required Structure

```
src/
├── domain/              # Business core (PURE)
├── application/         # Use cases and orchestration
├── infrastructure/      # Concrete implementations
└── adapters/            # External interfaces (CLI, HTTP)
```

### Dependency Rules

```
Domain ← Application ← Infrastructure
                    ← Adapters
```

| Layer | Can import | CANNOT import |
|-------|-----------|---------------|
| **Domain** | Nothing external | Application, Infrastructure, Adapters |
| **Application** | Domain, Ports (abstractions) | Infrastructure, Adapters |
| **Infrastructure** | Domain, Application | Adapters |
| **Adapters** | Domain, Application | Infrastructure (via Ports) |

### Base Classes

| Component | Layer | Base Class | Purpose |
|-----------|-------|------------|---------|
| Entity | Domain | `EntityBase` | Objects with identity |
| Value Object | Domain | `ValueObjectBase` | Immutable objects |
| UseCase | Application | `UseCaseBase` | Logic orchestration |
| Port | Application | `PortBase` | Contracts/abstractions |
| Adapter | Adapters | `AdapterBase` | I/O implementations |

---

## 2. CLI First

### Principle

**Every UseCase must be validated via CLI before being exposed via HTTP API.**

```
UseCase → CLIAdapter → Validated? → HTTPAdapter/WebUI
```

### Development Flow

```
1. Write UseCase
2. Expose via CLIAdapter
3. Test in the terminal
4. Automate CLI tests
5. Only then create HTTPAdapter/API
```

### Example

```python
# 1. UseCase
class CreateOrderUseCase(UseCaseBase):
    def execute(self, input): ...

# 2. CLI
cli = CLIAdapter(usecases={'create_order': CreateOrderUseCase(repo)})

# 3. Manual test
# $ python cli.py exec create_order --json '{"items": [...]}'

# 4. Only after: HTTP
@app.post("/orders")
def create_order(req):
    return usecase.execute(req)
```

### Benefits

- Automatic testability
- Fast debugging without a server
- Maintenance scripts
- Simplified CI/CD

---

## 3. Domain Exceptions

### Hierarchy

```python
from forge_base.domain.exceptions import (
    DomainException,        # Base for all
    ValidationError,        # Invalid data (format, type)
    InvariantViolation,     # Broken business rule
    BusinessRuleViolation,  # Operation not allowed
    EntityNotFoundError,    # Entity does not exist
    DuplicateEntityError,   # Duplicate entity
)
```

### When to Use Each

| Exception | When to use | Example |
|-----------|-------------|---------|
| `ValidationError` | Invalid data | Email without @ |
| `InvariantViolation` | Invalid state | Negative total |
| `BusinessRuleViolation` | Forbidden operation | Inactive user purchasing |
| `EntityNotFoundError` | Search with no result | Order does not exist |
| `DuplicateEntityError` | Uniqueness conflict | Email already registered |

### Example

```python
class CreateOrderUseCase(UseCaseBase):
    def execute(self, input):
        if not input.items:
            raise ValidationError("Order must have items")

        user = self.user_repo.find(input.user_id)
        if not user:
            raise EntityNotFoundError(f"User {input.user_id} not found")

        if not user.is_active:
            raise BusinessRuleViolation("Inactive user cannot create orders")
```

### Golden Rule

**Never use generic `Exception`.** Always use specific domain exceptions.

---

## 4. Observability

### Structured Logging

```python
from forge_base.observability.log_service import LogService

log = LogService(service_name="my-app", environment="production")
log.add_console_handler()
log.add_file_handler("logs/app.log")

# Structured log with context
log.info("Order created", order_id="123", user_id="456", total=99.90)

# With correlation ID (track request)
with log.correlation_context("req-abc-123"):
    log.info("Processing request")
    # all logs will have correlation_id
```

### Metrics

```python
from forge_base.observability.track_metrics import TrackMetrics

metrics = TrackMetrics()

# Counter
metrics.increment("orders.created", status="success")

# Timer (measures duration)
with metrics.timer("usecase.create_order_ms"):
    result = usecase.execute(input)

# Histogram
metrics.histogram("db.query_ms", 23.5, table="orders")

# Report
print(metrics.report())  # p50, p95, p99
```

### UseCase Pattern

```python
class CreateOrderUseCase(UseCaseBase):
    def __init__(self, repo, log, metrics):
        self.repo = repo
        self.log = log
        self.metrics = metrics

    def execute(self, input):
        with self.metrics.timer("usecase.create_order_ms"):
            try:
                # logic
                order = Order.create(input)
                self.repo.save(order)

                self.log.info("Order created", order_id=order.id)
                self.metrics.increment("orders.created", status="success")
                return order

            except DomainException as e:
                self.log.warning("Domain error", error=str(e))
                self.metrics.increment("orders.created", status="domain_error")
                raise
            except Exception as e:
                self.log.error("Unexpected error", error=str(e))
                self.metrics.increment("orders.created", status="error")
                raise
```

---

## 5. Code Quality

### Required Commands

```bash
# Before each commit
python devtool.py quality

# Or individually:
python devtool.py lint        # Ruff + Mypy
python devtool.py check-arch  # Validate layers
python devtool.py test        # Tests
python devtool.py check-deps  # Dependencies
```

### What Is Validated

| Tool | Validates |
|------|-----------|
| **Ruff** | Linting, formatting, imports |
| **Mypy** | Type hints, types |
| **import-linter** | Boundaries between layers |
| **deptry** | Unused dependencies |
| **pytest** | Tests passing |

---

## 6. Checklist for New Features

### Before Starting

- [ ] Do I understand the business requirement?
- [ ] Have I identified which layer will be affected?
- [ ] Do I need a new entity, UseCase, or Port?

### During Development

- [ ] Is business logic in the Domain?
- [ ] Does the UseCase only orchestrate, not implement I/O?
- [ ] Are Ports abstractions and Adapters implementations?
- [ ] Did I use specific domain exceptions?
- [ ] Did I add structured logs?
- [ ] Did I add relevant metrics?

### Before Commit

- [ ] Does `python devtool.py quality` pass?
- [ ] Does it work via CLI?
- [ ] Do tests cover success and error cases?
- [ ] Did I avoid introducing circular dependencies?

---

## 7. Anti-patterns to Avoid

### UseCase accessing the database directly

```python
# WRONG
class CreateOrderUseCase:
    def execute(self, input):
        conn = sqlite3.connect("db.sqlite")  # Direct I/O
        conn.execute("INSERT INTO orders...")
```

```python
# CORRECT
class CreateOrderUseCase:
    def __init__(self, order_repo: OrderRepositoryPort):  # Via Port
        self.order_repo = order_repo

    def execute(self, input):
        order = Order.create(input)
        self.order_repo.save(order)  # Abstraction
```

### Entity importing infrastructure

```python
# WRONG
from infrastructure.database import Database

class Order(EntityBase):
    def save(self):
        Database.insert(self)  # Entity should not do I/O
```

```python
# CORRECT
class Order(EntityBase):
    # Entity is pure, no I/O
    pass

# Repository handles I/O
class OrderRepository:
    def save(self, order: Order):
        self.db.insert(order)
```

### Business logic in Adapter

```python
# WRONG
@app.post("/orders")
def create_order(req):
    if req.total < 0:  # Validation in adapter
        raise HTTPException(400, "Invalid total")
    # logic here...  # Logic in adapter
```

```python
# CORRECT
@app.post("/orders")
def create_order(req):
    try:
        return usecase.execute(req)  # Delegates to UseCase
    except ValidationError as e:
        raise HTTPException(400, str(e))
```

### Generic Exception

```python
# WRONG
if not user:
    raise Exception("User not found")  # Generic
```

```python
# CORRECT
if not user:
    raise EntityNotFoundError(f"User {user_id} not found")  # Specific
```

### HTTP First

```python
# WRONG: Creating API without validating UseCase
@app.post("/orders")
def create_order(req):
    # Logic directly here, without testing first
```

```python
# CORRECT: CLI First
cli.run(['exec', 'create_order', '--json', '...'])  # Test first
# Then create HTTP
```

---

## 8. Test Structure

### Organization

```
tests/
├── unit/           # Isolated tests (mocks)
├── integration/    # Tests with real dependencies
├── property_based/ # Tests with Hypothesis
├── contract_tests/ # Contract tests between layers
└── cli/            # End-to-end tests via CLI
```

### Cognitive Test Example

```python
def test_order_creation_validates_minimum_items():
    """
    GIVEN an order with no items
    WHEN I try to create the order
    THEN it should fail with ValidationError

    Intention: Ensure that empty orders are rejected
    """
    usecase = CreateOrderUseCase(mock_repo)

    with pytest.raises(ValidationError) as exc:
        usecase.execute(CreateOrderInput(items=[]))

    assert "at least one item" in str(exc.value)
```

---

## 9. Useful Commands

```bash
# Development
python devtool.py scaffold usecase CreateOrder  # Generate boilerplate
python devtool.py discover                       # List components
python devtool.py test unit                      # Unit tests only

# Quality
python devtool.py quality   # Complete suite
python devtool.py lint      # Linting only
python devtool.py check-arch # Architecture only

# Application CLI
python cli.py list                              # List UseCases
python cli.py exec create_order --json '{...}' # Execute UseCase
```

---

## 10. References

- [Quick Start](quick-start.md) -- Installation
- [CLI First](cli-first.md) -- Detailed CLI First philosophy
- [Testing Guide](testing-guide.md) -- Cognitive tests
- [ForgeProcess](../reference/forge-process.md) -- Complete cognitive cycle
- [Architecture](../reference/architecture.md) -- Core modularization

---

**Version:** ForgeBase 0.1.5
**Updated:** 2025-12
