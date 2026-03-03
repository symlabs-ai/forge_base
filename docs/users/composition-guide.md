# Composition Root Guide

> "Those who use, don't create. Those who create, don't use."

The `composition` module implements the **Composition Root** pattern for declarative assembly of complex objects from configuration files (YAML, JSON, TOML).

---

## Fundamental Concepts

### What Is Composition Root?

Composition Root is the pattern where **all object assembly** happens in a single place, clearly separating:

- **Who creates**: The Builder assembles objects from specs
- **Who uses**: The rest of the code receives ready-made objects

### Module Components

| Component | Responsibility |
|-----------|----------------|
| `BuildSpecBase` | Declarative specification (YAML/JSON/TOML) |
| `PluginRegistryBase` | Plugin registry (kind, type_id) -> class |
| `BuildContextBase` | Build context with cache and env vars |
| `BuilderBase` | Orchestrates object assembly |
| `LoggerProtocol` | Protocol for loggers (low coupling) |
| `MetricsProtocol` | Protocol for metrics (low coupling) |

---

## Installation

The `composition` module is part of ForgeBase:

```python
from forge_base.composition import (
    BuildSpecBase,
    PluginRegistryBase,
    BuildContextBase,
    BuilderBase,
    LoggerProtocol,
    MetricsProtocol,
)
```

---

## Basic Usage

### 1. Define a BuildSpec

The BuildSpec defines the structure of your configuration:

```python
from dataclasses import dataclass, field
from typing import Any

from forge_base.composition import BuildSpecBase
from forge_base.domain.exceptions import ConfigurationError


@dataclass
class ServiceSpec(BuildSpecBase):
    """Specification for creating a service."""

    service: dict[str, Any] = field(default_factory=dict)
    database: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ServiceSpec":
        return cls(
            service=data.get("service", {}),
            database=data.get("database", {}),
            metadata=data.get("metadata", {}),
            observability=data.get("observability", {}),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "service": self.service,
            "database": self.database,
            "metadata": self.metadata,
            "observability": self.observability,
        }

    def validate(self) -> None:
        if not self.service.get("type"):
            raise ConfigurationError("service.type is required")
```

### 2. Create a PluginRegistry

The Registry maps types to concrete classes:

```python
from forge_base.composition import PluginRegistryBase


class DummyService:
    def __init__(self, name: str = "default"):
        self.name = name


class PostgresDB:
    def __init__(self, host: str = "localhost"):
        self.host = host


class ServiceRegistry(PluginRegistryBase):
    """Registry for services."""

    def register_defaults(self) -> None:
        # Register default plugins
        self.register("service", "dummy", DummyService)
        self.register("database", "postgres", PostgresDB)
```

### 3. Implement a Builder

The Builder orchestrates the assembly:

```python
from forge_base.composition import BuilderBase, BuildContextBase


class ServiceBuilder(BuilderBase[ServiceSpec, ServiceRegistry, BuildContextBase, DummyService]):
    """Builder for services."""

    def create_registry(self) -> ServiceRegistry:
        return ServiceRegistry()

    def create_context(self, spec: ServiceSpec) -> BuildContextBase:
        return BuildContextBase(spec=spec, registry=self.registry)

    def build(self, spec: ServiceSpec) -> DummyService:
        # Validate spec
        spec.validate()

        # Create context
        ctx = self.create_context(spec)

        # Resolve plugin from registry
        service_type = ctx.get("service.type", "dummy")
        service_cls = ctx.resolve("service", service_type)

        # Create instance
        name = ctx.get("service.name", "default")
        return service_cls(name=name)
```

### 4. Use the Builder

```python
# From dictionary
builder = ServiceBuilder()
service = builder.build_from_dict(
    {"service": {"type": "dummy", "name": "my-service"}},
    ServiceSpec
)

# From YAML
service = builder.build_from_yaml("config.yaml", ServiceSpec)

# From JSON
service = builder.build_from_json("config.json", ServiceSpec)

# From TOML
service = builder.build_from_toml("config.toml", ServiceSpec)

# Auto-detect format by extension
service = builder.build_from_file("config.yaml", ServiceSpec)
```

---

## Configuration File

### YAML (Recommended)

```yaml
# config.yaml
service:
  type: dummy
  name: my-service
  port: 8080

database:
  type: postgres
  host: localhost
  port: 5432

metadata:
  version: "1.0.0"
  author: "Team"

observability:
  log_level: info
  metrics_enabled: true
```

### JSON

```json
{
  "service": {
    "type": "dummy",
    "name": "my-service"
  },
  "database": {
    "type": "postgres"
  }
}
```

### TOML

```toml
[service]
type = "dummy"
name = "my-service"

[database]
type = "postgres"
```

---

## Advanced Features

### Path Navigation (Dot Notation)

The `BuildContext` allows accessing nested values using dot notation:

```python
ctx = BuildContextBase(spec=spec, registry=registry)

# Simple access
ctx.get("service")  # {"type": "dummy", "name": "my-service"}

# Nested access
ctx.get("service.type")  # "dummy"
ctx.get("service.port")  # 8080

# With default value
ctx.get("service.timeout", 30)  # 30 (if it doesn't exist)
```

### Object Cache

The context maintains a cache to avoid recreation:

```python
# First time: creates
if ctx.get_cached("db_connection") is None:
    conn = create_connection()
    ctx.set_cached("db_connection", conn)

# Second time: reuses
conn = ctx.get_cached("db_connection")
```

### Environment Variables

Environment variable resolution with precedence:

```python
# Priority system:
# 1. env_overrides (for tests)
# 2. os.environ (system)

# Required variable (raises if not found)
api_key = ctx.resolve_env("API_KEY")

# Optional variable
debug = ctx.resolve_env("DEBUG", required=False)

# Create new context with overrides (for tests)
test_ctx = ctx.with_env(
    API_KEY="test-key",
    DEBUG="true"
)
```

### Observability via Protocols

The Builder uses Protocols for low coupling:

```python
from forge_base.composition import LoggerProtocol, MetricsProtocol


class MyLogger:
    """Custom logger."""

    def info(self, message: str, **kwargs) -> None:
        print(f"INFO: {message}")

    def warning(self, message: str, **kwargs) -> None:
        print(f"WARN: {message}")

    def error(self, message: str, **kwargs) -> None:
        print(f"ERROR: {message}")

    def debug(self, message: str, **kwargs) -> None:
        print(f"DEBUG: {message}")


class MyMetrics:
    """Custom metrics."""

    def increment(self, name: str, value: int = 1, **tags) -> None:
        print(f"METRIC: {name} += {value}")

    def timing(self, name: str, value: float, **tags) -> None:
        print(f"TIMING: {name} = {value}ms")


# Use with Builder
builder = ServiceBuilder(
    log=MyLogger(),
    metrics=MyMetrics()
)
```

---

## Pattern for Derived Apps

Apps that depend on ForgeBase can expose their own Discovery API:

```python
# my_app/discovery.py
from forge_base.dev.api import ComponentDiscovery


class MyAppDiscovery(ComponentDiscovery):
    """Discovery for my application."""

    def __init__(self):
        # Scan only the installed package
        super().__init__(package_name="my_app")


# Usage by AI agents
discovery = MyAppDiscovery()
result = discovery.scan_project()

# View composition components
print(f"Registries: {len(result.registries)}")
print(f"Builders: {len(result.builders)}")
print(f"Specs: {len(result.specs)}")
```

---

## Complete Example

```python
"""Complete example of using the composition module."""

from dataclasses import dataclass, field
from typing import Any

from forge_base.composition import (
    BuildSpecBase,
    PluginRegistryBase,
    BuildContextBase,
    BuilderBase,
)
from forge_base.domain.exceptions import ConfigurationError


# 1. Domain service
class APIService:
    def __init__(self, name: str, port: int = 8080):
        self.name = name
        self.port = port

    def start(self) -> None:
        print(f"Starting {self.name} on port {self.port}")


# 2. Spec
@dataclass
class APISpec(BuildSpecBase):
    api: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "APISpec":
        return cls(
            api=data.get("api", {}),
            metadata=data.get("metadata", {}),
            observability=data.get("observability", {}),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "api": self.api,
            "metadata": self.metadata,
            "observability": self.observability,
        }

    def validate(self) -> None:
        if not self.api.get("name"):
            raise ConfigurationError("api.name is required")


# 3. Registry
class APIRegistry(PluginRegistryBase):
    def register_defaults(self) -> None:
        self.register("api", "rest", APIService)


# 4. Builder
class APIBuilder(BuilderBase[APISpec, APIRegistry, BuildContextBase, APIService]):
    def create_registry(self) -> APIRegistry:
        return APIRegistry()

    def create_context(self, spec: APISpec) -> BuildContextBase:
        return BuildContextBase(spec=spec, registry=self.registry)

    def build(self, spec: APISpec) -> APIService:
        spec.validate()
        ctx = self.create_context(spec)

        service_cls = ctx.resolve("api", ctx.get("api.type", "rest"))
        return service_cls(
            name=ctx.get("api.name"),
            port=ctx.get("api.port", 8080)
        )


# 5. Usage
if __name__ == "__main__":
    # Create builder
    builder = APIBuilder()

    # Build from dict
    api = builder.build_from_dict(
        {"api": {"name": "my-api", "port": 3000}},
        APISpec
    )

    # Use
    api.start()  # Starting my-api on port 3000
```

---

## Component Discovery

`ComponentDiscovery` automatically detects composition components:

```python
from forge_base.dev.api import ComponentDiscovery

discovery = ComponentDiscovery()
result = discovery.scan_project()

# List registries
for reg in result.registries:
    print(f"Registry: {reg.name} at {reg.file_path}:{reg.line_number}")

# List builders
for builder in result.builders:
    print(f"Builder: {builder.name} at {builder.file_path}:{builder.line_number}")

# List specs
for spec in result.specs:
    print(f"Spec: {spec.name} at {spec.file_path}:{spec.line_number}")
```

---

## Best Practices

1. **One Builder per Domain**: Create specific builders for each domain (ServiceBuilder, PipelineBuilder, etc.)

2. **Validatable Specs**: Always implement `validate()` to detect errors early

3. **Sensible Defaults**: Register default plugins in `register_defaults()`

4. **Tests with env_overrides**: Use `with_env()` to inject variables in tests

5. **Protocols for Observability**: Use `LoggerProtocol` and `MetricsProtocol` for low coupling

---

## Next Steps

- [Architecture](../reference/architecture.md) -- Framework structure
- [ForgeProcess](../reference/forge-process.md) -- Complete cognitive cycle
- [Recipes](recipes.md) -- Patterns and practical examples

---

**"Composition is the secret of modularity."**
