# CLI First -- Development Philosophy

> "If it doesn't work in the terminal, it doesn't work anywhere."

## The Principle

**CLI First** means that every UseCase must be validated via command line before being exposed via HTTP API, WebSocket, or any other interface.

```
UseCase → CLIAdapter → Validated? → HTTPAdapter/WebUI
```

## Why CLI First?

| Benefit | Description |
|---------|-------------|
| **Testability** | CLI is trivial to automate in scripts and CI/CD |
| **Speed** | Test without spinning up a server, database, or frontend |
| **Isolation** | Validates business logic without UI dependencies |
| **Automation** | Integration with pipelines, cron jobs, scripts |
| **Debug** | Direct output, without abstraction layers |
| **Living documentation** | `--help` documents what the system does |

## Development Flow

```
1. Write UseCase (domain + application)
2. Expose via CLIAdapter
3. Test manually in the terminal
4. Automate CLI tests
5. Validate with user/stakeholder via CLI
6. Only then create HTTPAdapter/API/UI
```

## Implementation in ForgeBase

### 1. Create the UseCase

```python
# src/application/usecases/create_order.py
from forge_base.application import UseCaseBase
from dataclasses import dataclass

@dataclass
class CreateOrderInput:
    customer_id: str
    items: list[dict]

@dataclass
class CreateOrderOutput:
    order_id: str
    total: float

class CreateOrderUseCase(UseCaseBase[CreateOrderInput, CreateOrderOutput]):
    def __init__(self, order_repo, product_repo):
        self.order_repo = order_repo
        self.product_repo = product_repo

    def execute(self, input: CreateOrderInput) -> CreateOrderOutput:
        # Validation
        if not input.items:
            raise ValidationError("Order must have at least one item")

        # Business logic
        order = Order.create(
            customer_id=input.customer_id,
            items=input.items
        )

        self.order_repo.save(order)

        return CreateOrderOutput(
            order_id=order.id,
            total=order.total
        )
```

### 2. Expose via CLIAdapter

```python
# src/cli.py
from forge_base.adapters.cli import CLIAdapter
from application.usecases.create_order import CreateOrderUseCase
from infrastructure.repositories import OrderRepository, ProductRepository

# Initialize dependencies
order_repo = OrderRepository()
product_repo = ProductRepository()

# Register UseCases
cli = CLIAdapter(usecases={
    'create_order': CreateOrderUseCase(order_repo, product_repo),
    'list_orders': ListOrdersUseCase(order_repo),
    'cancel_order': CancelOrderUseCase(order_repo),
})

if __name__ == '__main__':
    cli.run()
```

### 3. Test in the Terminal

```bash
# List available commands
python src/cli.py list

# Create an order
python src/cli.py exec create_order --json '{
  "customer_id": "cust-123",
  "items": [
    {"product_id": "prod-1", "quantity": 2},
    {"product_id": "prod-2", "quantity": 1}
  ]
}'

# Output (structured JSON)
{
  "result": {
    "order_id": "ord-abc-123",
    "total": 150.00
  }
}
```

### 4. Automate Tests

```python
# tests/cli/test_create_order_cli.py
import subprocess
import json

def test_create_order_via_cli():
    """End-to-end test via CLI."""
    result = subprocess.run(
        [
            'python', 'src/cli.py', 'exec', 'create_order',
            '--json', '{"customer_id": "test", "items": [{"product_id": "p1", "quantity": 1}]}'
        ],
        capture_output=True,
        text=True
    )

    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert 'order_id' in output['result']

def test_create_order_empty_items_fails():
    """Order without items should fail."""
    result = subprocess.run(
        [
            'python', 'src/cli.py', 'exec', 'create_order',
            '--json', '{"customer_id": "test", "items": []}'
        ],
        capture_output=True,
        text=True
    )

    assert result.returncode == 1
    assert 'at least one item' in result.stderr
```

### 5. Only After: HTTP/API

```python
# src/api.py
from fastapi import FastAPI
from application.usecases.create_order import CreateOrderUseCase, CreateOrderInput

app = FastAPI()

@app.post("/orders")
def create_order(input: CreateOrderInput):
    # Same UseCase, different adapter
    usecase = CreateOrderUseCase(order_repo, product_repo)
    result = usecase.execute(input)
    return {"order_id": result.order_id, "total": result.total}
```

## Project Pattern

```
src/
├── domain/              # Entities, business rules
├── application/
│   └── usecases/        # Pure UseCases
├── infrastructure/      # Repositories, configs
├── adapters/
│   ├── cli/             # CLI (first!)
│   └── http/            # HTTP (after)
└── cli.py               # CLI entry point
```

## CLI First Checklist

Before creating an HTTP API, validate:

- [ ] Does the UseCase work via CLI?
- [ ] Do errors return clear messages?
- [ ] Is the output structured JSON?
- [ ] Does `--help` document the parameters?
- [ ] Do CLI tests pass?
- [ ] Has the stakeholder validated the behavior?

## Benefits in Production

### Maintenance Scripts

```bash
# Cron job for cleanup
0 2 * * * python cli.py exec cleanup_old_orders --json '{"days": 90}'

# Migration script
python cli.py exec migrate_users --json '{"batch_size": 100}'
```

### CI/CD

```yaml
# .github/workflows/test.yml
- name: Test CLI
  run: |
    python cli.py exec health_check
    python cli.py exec create_order --json '{"customer_id": "test", "items": [...]}'
```

### Debugging in Production

```bash
# SSH into the server
python cli.py exec get_order --json '{"order_id": "ord-123"}'
python cli.py exec retry_payment --json '{"order_id": "ord-123"}'
```

## Anti-patterns

### Wrong: HTTP First

```python
# Creating API without validating UseCase
@app.post("/orders")
def create_order(req):
    # Logic mixed with HTTP
    # Hard to test
    # Hard to reuse
    pass
```

### Correct: CLI First

```python
# 1. Pure UseCase
class CreateOrderUseCase:
    def execute(self, input): ...

# 2. CLI validates
cli.run(['exec', 'create_order', '--json', '...'])

# 3. HTTP reuses
@app.post("/orders")
def create_order(req):
    return usecase.execute(req)
```

## Integration with ForgeProcess

CLI First is **Phase 4** of the ForgeProcess cognitive cycle:

```
MDD → BDD → TDD → CLI → Feedback
                   ↑
              You are here
```

Before delivering to users (Feedback), validate via CLI.

---

**References:**
- [CLIAdapter](../reference/architecture.md) -- Adapter implementation
- [ForgeProcess](../reference/forge-process.md) -- Complete cycle
- [UseCaseBase](../reference/architecture.md) -- Base for use cases
