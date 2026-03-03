# ForgeBase

**ForgeBase** is the technical core of the Forge Framework — the cognitive infrastructure where ForgeProcess reasoning is transformed into observable, reflexive, and modular code.

---

## For AI Coding Agents

**First time using ForgeBase?** Access complete API documentation programmatically:

```python
from forge_base.dev import get_agent_quickstart

# Get the full AI Agent Quick Start guide (embedded in package)
guide = get_agent_quickstart()
print(guide)  # Full markdown with examples and API reference
```

**Available APIs for AI Agents:**

```python
from forge_base.dev.api import (
    QualityChecker,      # Code quality checks (ruff, mypy)
    ScaffoldGenerator,   # Generate boilerplate code
    ComponentDiscovery,  # Discover entities, usecases, ports
    TestRunner          # Run tests programmatically
)

# Example: Quality check before commit
checker = QualityChecker()
results = checker.run_all()

for tool, result in results.items():
    if not result.passed:
        for error in result.errors:
            # Each error has: file, line, column, code, message
            print(f"Fix {error['file']}:{error['line']} - {error['code']}")
```

**Why this matters:**
- Works offline (docs embedded in package)
- Structured, machine-readable results (not CLI text parsing)
- Auto-discovery of components and architecture
- Integrated quality checking and code generation

**Complete guide:** See [docs/ai-agents/](docs/ai-agents/) for full documentation with error codes, data structures, and workflow examples.

---

## Quick Start

### Installation

```bash
# Install from GitHub
pip install git+https://github.com/symlabs-ai/forge_base.git

# Or clone for development
git clone https://github.com/symlabs-ai/forge_base.git
cd forge_base
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

### For AI Agents (Programmatic Access)

```python
# Documentation is embedded in the package - works offline!
from forge_base.dev import get_agent_quickstart

guide = get_agent_quickstart()  # Full API documentation
# Parse and use to discover available APIs
```

### For Developers (CLI)

```bash
# Run quality checks
python devtool.py quality

# Generate boilerplate
python devtool.py scaffold usecase CreateOrder

# Run tests
python devtool.py test
```

---

## Repository Structure

```
forge_base/
├── docs/                 # Complete documentation (reorganized)
│   ├── users/            # Guides for human developers
│   ├── ai-agents/        # Documentation for AI agents
│   ├── reference/        # Technical reference and architecture
│   └── adr/              # Architecture Decision Records
├── examples/             # Framework usage examples
├── scripts/              # Development scripts (scaffolding, discovery)
├── src/                  # ForgeBase framework source code
│   └── forge_base/
│       ├── domain/           # Domain Layer
│       ├── application/      # Application Layer
│       ├── infrastructure/   # Infrastructure Layer
│       ├── integration/      # Adapters and integrations
│       └── observability/    # Observability system
├── tests/                # Tests (unit, integration, property-based, contract)
├── devtool.py           # Unified development CLI
├── pyproject.toml       # Project configuration (PEP 621)
├── setup.py             # Shim for backward compatibility
├── CHANGELOG.md         # Change history
├── CONTRIBUTING.md      # Contribution guide
├── VERSION.MD           # Current project version
└── README.md            # This file
```

### Folder Details

#### `docs/`
Complete project documentation, organized by target audience:
- **users/** — Guides for developers (quick start, recipes, testing)
- **ai-agents/** — Documentation for AI agents (APIs, discovery, ecosystem)
- **reference/** — Technical reference (ForgeProcess, architecture)
- **adr/** — Architecture Decision Records

#### `examples/`
Practical framework usage examples:
- **user_management/** — Complete user management system
  - Demonstrates Clean Architecture in practice
  - Includes domain (User, Email), application (CreateUserUseCase), and infrastructure (JSONUserRepository)

#### `scripts/`
Development tools:
- **scaffold.py** — Boilerplate generator (UseCases, Ports, Adapters)
- **discover.py** — Component discovery and cataloging
- **mypy.ini** — Type checking configuration

#### `src/forge_base/`
Source code following Clean + Hexagonal Architecture:

**`domain/`** — Domain Layer (business core)
- `entity_base.py` — Base class for entities with immutable identity
- `value_object_base.py` — Base class for immutable value objects
- `exceptions.py` — Business exceptions (BusinessRuleViolation, ValidationError)

**`application/`** — Application Layer (orchestration)
- `usecase_base.py` — Generic base class for use cases
- `port_base.py` — Base class for ports (I/O abstractions)
- `dto_base.py` — Base class for DTOs (Data Transfer Objects)

**`infrastructure/`** — Infrastructure Layer (implementations)
- `config/` — Configuration management (YAML, environment)
- `repository/` — Repository Pattern implementations
  - `repository_base.py` — Abstract Repository Pattern interface
  - `json_repository.py` — Repository with JSON storage (dev/testing)
  - `sql_repository.py` — Repository with SQLAlchemy (production)

**`integration/`** — External adapters
- Adapters for external systems, APIs, etc.

**`observability/`** — Native observability system
- Decorators and utilities for metrics, logging, and tracing

#### `tests/`
Complete test suite:
- **unit/** — Isolated unit tests
- **integration/** — Inter-component integration tests
- **property_based/** — Property-based tests (Hypothesis)
- **contract_tests/** — Contract tests between layers

#### `devtool.py`
Unified development CLI:
```bash
python devtool.py scaffold      # Generate boilerplate
python devtool.py discover      # Catalog components
python devtool.py test          # Run tests
python devtool.py lint          # Linters (Ruff, Mypy)
python devtool.py check-deps    # Validate dependencies
python devtool.py check-arch    # Validate architecture
python devtool.py quality       # Full quality suite
```

### Configuration Files

#### `pyproject.toml`
Modern configuration following PEP 621:
- Project metadata and dependencies
- Tool configuration (pytest, mypy, ruff, coverage, deptry)
- Single source of truth for the entire project

#### `.import-linter`
Clean Architecture boundary validation:
- Ensures layers do not violate dependencies
- Domain cannot import Application/Infrastructure
- Application cannot import Infrastructure

#### `VERSION.MD`
Current project version tracking

#### `CHANGELOG.md`
Detailed change history by version

---

## Philosophy

> "To forge is to transform thought into structure."

ForgeBase is not just a technical framework — it is a **cognitive architecture** that:
- **Thinks**: Each component carries intention and purpose
- **Measures**: Native observability at all levels
- **Explains**: Self-reflection and living documentation capability

### Core Principles

1. **Reflexivity** — Code understands and explains its own workings
2. **Autonomy** — Independent modules with well-defined contracts
3. **Cognitive Coherence** — Consistent patterns across the entire architecture

---

## Project Status

**Current Version:** v0.1.2 (Production-Ready)

### Complete (PHASE 1 - Foundation)

**Domain Layer**
- EntityBase with immutable ID (property-based)
- ValueObjectBase with structural equality
- Business exceptions (BusinessRuleViolation, ValidationError)

**Application Layer**
- Generic UseCaseBase (Generic[TInput, TOutput])
- PortBase for I/O abstractions
- DTOBase for data transfer

**Infrastructure Layer**
- RepositoryBase (DDD Repository Pattern)
- JSONRepository (thread-safe, development/testing)
- SQLRepository (SQLAlchemy, production-ready)
- ConfigLoader (YAML + environment variables)

**Developer Tooling**
- devtool.py (unified CLI)
- Scaffolding (boilerplate generation)
- Discovery (component cataloging)
- Modern dependency management (pyproject.toml)
- Import standardization (100% absolute imports)
- Cross-platform support

**Quality Assurance**
- 84+ tests passing (unit + integration + property-based + contract)
- Mypy strict type checking
- Ruff linting + pre-commit hooks
- Import-linter (architecture boundary validation)
- Deptry (dependency hygiene)

### In Development (PHASE 2)

**Observability**
- Native metrics
- Observability decorators
- Structured logging system

**Integration Layer**
- External system adapters
- API adapters (REST, GraphQL)

### Backlog

See [CHANGELOG.md](/CHANGELOG.md) for detailed change history.

See [CHANGELOG.md](/CHANGELOG.md) for detailed change history.

---

## Documentation

For a complete understanding of the architecture, see:

### For Developers
- [Quick Start](/docs/users/quick-start.md) — Installation and first steps
- [Recipes](/docs/users/recipes.md) — Practical usage examples
- [Testing Guide](/docs/users/testing-guide.md) — How to run and write tests

### For AI Agents
- [Quick Start](/docs/ai-agents/quick-start.md) — Quick start for AI agents
- [Complete Guide](/docs/ai-agents/complete-guide.md) — Full API reference
- [Discovery](/docs/ai-agents/discovery.md) — API discovery system
- [Ecosystem](/docs/ai-agents/ecosystem.md) — Tool integration

### Technical Reference
- [ForgeProcess](/docs/reference/forge-process.md) — Cognitive development cycle
- [Architecture](/docs/reference/architecture.md) — Core modularization

---
## IMPORTANT NOTICES
- Never write anything to the root without explicit user request
- Never push to the remote repository without explicit user request
- Never create tags or bump forge_base version without explicit user request
- The source of truth for the current version, as well as synthetic history, can be found in VERSION.md

## Technologies

- **Python 3.11+**
- **Clean Architecture** + **Hexagonal Architecture**
- **Native Observability** (Logging, Metrics, Tracing)
- **Test-Driven Development**

---
