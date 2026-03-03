# ForgeBase Derived Apps and AI Agents

> How to create apps that expose a standard experience for code agents, reusing the ForgeBase ecosystem.

This guide is for those who **build a new application using ForgeBase as a foundation** and want:

- AI agents to be able to discover the app's APIs in a standardized way;
- clients who install the app via `pip install my_app` to have the same discovery experience that already exists in ForgeBase.

---

## Design Goal

For each ForgeBase-derived app, we want:

- a `my_app.dev` module dedicated to AI agents;
- a built-in quick start guide (`get_agent_quickstart()`), just like ForgeBase's;
- a discovery API that scans **only the app's package**, not ForgeBase internals;
- a standard section in the `README.md` explaining this to agents.

This way, any agent that has learned to use ForgeBase also knows how to use your app.

---

## Recommended Project Structure

Assume an app called `my_app`:

```text
src/
  my_app/
    __init__.py
    domain/
    application/
    adapters/
    infrastructure/
    _docs/
      AI_AGENT_QUICK_START.md
    dev/
      __init__.py
      api/
        __init__.py
        discovery.py
```

- `my_app._docs/AI_AGENT_QUICK_START.md`: quick start guide for AI agents (for your app).
- `my_app.dev`: entry point for agents (`get_agent_quickstart`, `get_documentation_path`, etc.).
- `my_app.dev.api`: here you re-export discovery, quality checks, tests, etc.

---

## Step 1 -- `my_app.dev` with `get_agent_quickstart`

Implement in `src/my_app/dev/__init__.py` something inspired by ForgeBase:

```python
# src/my_app/dev/__init__.py
import importlib.resources as resources
from pathlib import Path


def get_agent_quickstart() -> str:
    """Returns the quick start guide for AI agents of your app."""
    try:
        if hasattr(resources, "files"):
            doc_file = resources.files("my_app._docs") / "AI_AGENT_QUICK_START.md"
            return doc_file.read_text(encoding="utf-8")
    except (FileNotFoundError, ModuleNotFoundError, AttributeError):
        pass

    # Development fallback (optional)
    project_root = Path(__file__).parent.parent.parent
    quickstart_path = project_root / "docs" / "users" / "my_app_quickstart.md"
    if quickstart_path.exists():
        return quickstart_path.read_text(encoding="utf-8")

    return "# Agent Quickstart\n\nDocumentation not found."
```

In your `AI_AGENT_QUICK_START.md`, clearly document:

- the app's main APIs;
- how to run discovery;
- how to run the app's own tests and quality checks.

---

## Step 2 -- App-specific discovery API

Instead of each project reinventing discovery, reuse the ForgeBase mechanism via `ComponentDiscovery`, now with `package_name` support.

Create `src/my_app/dev/api/discovery.py`:

```python
# src/my_app/dev/api/discovery.py
from forge_base.dev.api import ComponentDiscovery as BaseComponentDiscovery


class ComponentDiscovery(BaseComponentDiscovery):
    """Discovery for my_app package components.

    Scans only the app's code, even when installed via pip.
    """

    def __init__(self) -> None:
        # package_name -> resolves the installed package path (site-packages or src/)
        super().__init__(package_name="my_app")
```

Then, in `src/my_app/dev/api/__init__.py`, re-export this class:

```python
# src/my_app/dev/api/__init__.py
from .discovery import ComponentDiscovery

__all__ = ["ComponentDiscovery"]
```

Usage within the app or by client agents:

```python
from my_app.dev.api import ComponentDiscovery

discovery = ComponentDiscovery()
result = discovery.scan_project()

for usecase in result.usecases:
    print(usecase.name, usecase.file_path)
```

This ensures that:

- only `my_app` is scanned (not ForgeBase internals);
- it works the same in development and in production (installed via `pip`).

---

## Step 3 -- Reuse other ForgeBase APIs (optional)

If it makes sense for your app, you can also re-export:

- `QualityChecker` (for checks specific to your repo),
- `TestRunner` (for running your project's tests),
- `ScaffoldGenerator` (if you have your own scaffolds).

Simple example:

```python
# src/my_app/dev/api/__init__.py
from forge_base.dev.api import QualityChecker, TestRunner
from .discovery import ComponentDiscovery

__all__ = [
    "ComponentDiscovery",
    "QualityChecker",
    "TestRunner",
]
```

Document in your `AI_AGENT_QUICK_START.md` how these APIs apply to your project.

---

## Step 4 -- Standard section in your app's README

Add an explicit section for agents in your app's `README.md`, following the ForgeBase pattern:

```markdown
## For AI Code Agents

```python
from my_app.dev import get_agent_quickstart

guide = get_agent_quickstart()  # Complete Markdown with app APIs
print(guide)
```

### App component discovery

```python
from my_app.dev.api import ComponentDiscovery

discovery = ComponentDiscovery()
result = discovery.scan_project()
print(f"UseCases found: {len(result.usecases)}")
```
```

This ensures that:

- agents that only read the `README.md` know how to get started;
- the experience is consistent with ForgeBase.

---

## Step 5 -- How your client agents will use it

Once your app is published and installed via `pip`, the typical flow for an agent is:

```python
from my_app.dev import get_agent_quickstart
from my_app.dev.api import ComponentDiscovery

# 1. Read the app's quick start guide
guide = get_agent_quickstart()

# 2. Discover app-specific components
discovery = ComponentDiscovery()
components = discovery.scan_project()

print("Entities:", [e.name for e in components.entities])
print("UseCases:", [u.name for u in components.usecases])
```

No agent needs to know details about your repo's folder layout -- everything is exposed via stable APIs.

---

## Complete Example: `orders_app`

To make everything more concrete, below is a minimal example of a derived app called `orders_app`.

### Folder Structure

```text
src/
  orders_app/
    __init__.py
    domain/
      order.py
    application/
      create_order_usecase.py
    _docs/
      AI_AGENT_QUICK_START.md
    dev/
      __init__.py
      api/
        __init__.py
        discovery.py
```

### `orders_app/domain/order.py`

```python
from forge_base.domain import EntityBase


class Order(EntityBase):
    """Order domain entity."""

    def __init__(self, id: str | None, customer_id: str, total: float) -> None:
        super().__init__(id)
        self.customer_id = customer_id
        self.total = total

    def validate(self) -> None:
        if not self.customer_id:
            raise ValueError("customer_id is required")
        if self.total < 0:
            raise ValueError("total cannot be negative")
```

### `orders_app/application/create_order_usecase.py`

```python
from forge_base.application import UseCaseBase


class CreateOrderInput:
    def __init__(self, customer_id: str, total: float) -> None:
        self.customer_id = customer_id
        self.total = total


class CreateOrderOutput:
    def __init__(self, order_id: str) -> None:
        self.order_id = order_id


class CreateOrderUseCase(UseCaseBase[CreateOrderInput, CreateOrderOutput]):
    """Order creation UseCase."""

    def _before_execute(self) -> None:
        pass

    def _after_execute(self) -> None:
        pass

    def _on_error(self, error: Exception) -> None:
        raise error

    def execute(self, input_dto: CreateOrderInput) -> CreateOrderOutput:
        # Here you would use a real repository; for example, generates a fixed ID
        if input_dto.total <= 0:
            raise ValueError("total must be greater than zero")
        order_id = "order-123"
        return CreateOrderOutput(order_id=order_id)
```

### `orders_app/dev/__init__.py`

```python
import importlib.resources as resources
from pathlib import Path


def get_agent_quickstart() -> str:
    """Quick start guide for orders_app AI agents."""
    try:
        if hasattr(resources, "files"):
            doc_file = resources.files("orders_app._docs") / "AI_AGENT_QUICK_START.md"
            return doc_file.read_text(encoding="utf-8")
    except (FileNotFoundError, ModuleNotFoundError, AttributeError):
        pass

    project_root = Path(__file__).parent.parent.parent
    quickstart_path = project_root / "docs" / "users" / "orders_app_quickstart.md"
    if quickstart_path.exists():
        return quickstart_path.read_text(encoding="utf-8")

    return "# orders_app Quickstart\n\nDocumentation not found."
```

### `orders_app/dev/api/discovery.py`

```python
from forge_base.dev.api import ComponentDiscovery as BaseComponentDiscovery


class ComponentDiscovery(BaseComponentDiscovery):
    """Discovery for orders_app package components."""

    def __init__(self) -> None:
        super().__init__(package_name="orders_app")
```

### `orders_app/dev/api/__init__.py`

```python
from .discovery import ComponentDiscovery

__all__ = ["ComponentDiscovery"]
```

### `orders_app/_docs/AI_AGENT_QUICK_START.md`

```markdown
# orders_app - Quick Start Guide for AI Agents

```python
from orders_app.dev import get_agent_quickstart
from orders_app.dev.api import ComponentDiscovery

guide = get_agent_quickstart()
discovery = ComponentDiscovery()
result = discovery.scan_project()

print("Entities:", [e.name for e in result.entities])
print("UseCases:", [u.name for u in result.usecases])
```
```

With this structure, any agent can:

- discover the app's documentation via `get_agent_quickstart()`;
- discover `orders_app`-specific components via `orders_app.dev.api.ComponentDiscovery`;
- apply the same patterns it already uses with ForgeBase.

---

## Summary

- Use `forge_base.dev.api.ComponentDiscovery(package_name="my_app")` as the base for your app's discovery.
- Always expose a `my_app.dev` module with `get_agent_quickstart()`.
- Replicate the ForgeBase README pattern to explain this to agents.
- This way, any ForgeBase-derived app offers a consistent and predictable experience for AI agents, both in development and in production.
