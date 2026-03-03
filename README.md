# ForgeBase

**ForgeBase** is the technical core of the Forge Framework — the cognitive infrastructure where ForgeProcess reasoning becomes observable, reflective, and modular code.

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

See [docs/ai-agents/](docs/ai-agents/) for full documentation with error codes, data structures, and workflow examples.

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
├── docs/                 # Full documentation (organized by audience)
│   ├── users/            # Guides for human developers
│   ├── ai-agents/        # Documentation for AI agents
│   ├── reference/        # Technical reference and architecture
│   └── adr/              # Architecture Decision Records
├── examples/             # Framework usage examples
│   ├── ai_agent_usage.py
│   ├── claude_api_integration.py
│   ├── complete_flow.py
│   ├── integration_demo.py
│   └── user_management/  # Full user management system (Clean Architecture)
├── scripts/              # Development scripts (scaffolding, discovery)
├── src/                  # ForgeBase framework source code
│   └── forge_base/
│       ├── adapters/         # Cross-cutting adapters
│       ├── application/      # Application Layer (orchestration)
│       ├── composition/      # Composition root and dependency wiring
│       ├── domain/           # Domain Layer (business core)
│       ├── infrastructure/   # Infrastructure Layer (implementations)
│       ├── integration/      # External adapters and integrations
│       ├── observability/    # Native observability system
│       ├── pulse/            # ForgePulse — operational telemetry
│       └── testing/          # Testing utilities and helpers
├── tests/                # Tests (unit, integration, property-based, contract, benchmarks)
│   ├── unit/
│   ├── integration/
│   ├── property_based/
│   ├── contract_tests/
│   └── benchmarks/
├── devtool.py           # Unified development CLI
├── pyproject.toml       # Project configuration (PEP 621)
├── CHANGELOG.md         # Change history
├── CONTRIBUTING.md      # Contribution guide
├── VERSION.MD           # Current project version
└── README.md            # This file
```

### Source Layout (`src/forge_base/`)

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
  - `json_repository.py` — JSON storage repository (dev/testing)
  - `sql_repository.py` — SQLAlchemy repository (production)

**`adapters/`** — Cross-cutting adapters

**`composition/`** — Composition root and dependency wiring

**`integration/`** — External system adapters

**`observability/`** — Native observability system (decorators, structured logging, metrics)

**`pulse/`** — ForgePulse operational telemetry (6 phases shipped)
- Sampling policies, budget governance, span tracing, export pipelines
- Level differentiation, DashboardSummary, tag propagation

**`testing/`** — Testing utilities and helpers

### `devtool.py` — Unified CLI

```bash
python devtool.py scaffold      # Generate boilerplate
python devtool.py discover      # Catalog components
python devtool.py test          # Run tests
python devtool.py lint          # Linters (Ruff, Mypy)
python devtool.py check-deps    # Validate dependencies
python devtool.py check-arch    # Validate architecture
python devtool.py check-types   # Run type checking with mypy
python devtool.py quality       # Full quality suite (lint + test + deps + arch)
```

---

## Philosophy

> "To forge is to transform thought into structure."

ForgeBase is not just a technical framework — it is a **cognitive architecture** that:
- **Thinks**: Every component carries intention and purpose
- **Measures**: Native observability at every level
- **Explains**: Self-reflection and living documentation

### Core Principles

1. **Reflexivity** — Code understands and explains its own behavior
2. **Autonomy** — Independent modules with well-defined contracts
3. **Cognitive Coherence** — Consistent patterns across the entire architecture

---

## Project Status

**Current Version:** v0.3.6 (Production-Ready)

### Complete — Foundation

**Domain Layer**
- EntityBase with immutable ID (property-based tested)
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

**Adapters & Composition**
- Cross-cutting adapters module
- Composition root for dependency wiring

### Complete — Observability & ForgePulse

**ForgePulse** — Full operational telemetry (6 phases shipped):
- Phase 1: Core metric recording and track system
- Phase 2: CL/CE classification and event model
- Phase 3: `@pulse_meta` decorator for subtrack/trace precision
- Phase 4: Governance — SamplingPolicy, ECM, AsyncBuffer
- Phase 5: Tracing + export — SpanRecord, BudgetPolicy, ExportPipeline
- Phase 6: Level differentiation, DashboardSummary, tag propagation

### Complete — Developer Tooling

- devtool.py (unified CLI)
- Scaffolding (boilerplate generation)
- Discovery (component cataloging)
- Modern dependency management (pyproject.toml)
- Import standardization (100% absolute imports)
- Cross-platform support

### Complete — Quality Assurance

- 608+ test functions across 51 files (unit + integration + property-based + contract + benchmarks)
- Mypy strict type checking
- Ruff linting + pre-commit hooks
- Import-linter (architecture boundary validation)
- Deptry (dependency hygiene)

### Complete — Testing Module

- Testing utilities and helpers for ForgeBase consumers

---

## Documentation

### For Developers
- [ForgeBase Rules](/docs/users/forgebase-rules.md) — Complete rules and practices guide
- [Quick Start](/docs/users/quick-start.md) — Installation and first steps
- [Recipes](/docs/users/recipes.md) — Practical usage examples
- [Testing Guide](/docs/users/testing-guide.md) — Running and writing tests
- [CLI First](/docs/users/cli-first.md) — CLI First development philosophy
- [Environment & Scripts](/docs/users/environment-and-scripts.md) — Environment setup and tools
- [Extending ForgeBase](/docs/users/extending-forgebase.md) — How to extend ForgeBase
- [Composition Guide](/docs/users/composition-guide.md) — Composition root patterns
- [ForgePulse Quick Start](/docs/users/pulse_quick_start.md) — Getting started with ForgePulse
- [ForgePulse Cookbook](/docs/users/pulse_cookbook.md) — ForgePulse recipes and patterns

### For AI Agents
- [Quick Start](/docs/ai-agents/quick-start.md) — Quick start for AI agents
- [Full Guide](/docs/ai-agents/complete-guide.md) — Complete API reference
- [Discovery](/docs/ai-agents/discovery.md) — API discovery system
- [Ecosystem](/docs/ai-agents/ecosystem.md) — Tool integration

### Technical Reference
- [ForgeProcess](/docs/reference/forge-process.md) — Cognitive development cycle
- [Architecture](/docs/reference/architecture.md) — Core modularization
- [Documentation Guide](/docs/reference/documentation_guide.md) — Docstring standards

### Examples
- [`ai_agent_usage.py`](/examples/ai_agent_usage.py) — AI agent integration example
- [`claude_api_integration.py`](/examples/claude_api_integration.py) — Claude API integration
- [`complete_flow.py`](/examples/complete_flow.py) — End-to-end flow demonstration
- [`integration_demo.py`](/examples/integration_demo.py) — Integration demo
- [`user_management/`](/examples/user_management/) — Full user management system (Clean Architecture)

---

## IMPORTANT NOTICES

- Never write files to the repository root without explicit user request
- Never push to the remote repository without explicit user request
- Never create tags or bump the ForgeBase version without explicit user request
- The source of truth for the current version and synthetic history is VERSION.md

---

## Technologies

- **Python 3.11+**
- **Clean Architecture** + **Hexagonal Architecture**
- **Native Observability** (Logging, Metrics, Tracing via ForgePulse)
- **Test-Driven Development**

---
