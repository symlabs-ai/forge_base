# PRD — ForgeBase Core Modularization

## Overview

This document describes the modularization plan for the **ForgeBase core**, the central technical component of the **Forge Framework**.
The goal is to establish a stable, extensible, and observable structure, ensuring coherence between the **architectural reasoning (ForgeProcess)** and its **technical execution (ForgeBase)**.

The modularization aims to consolidate ForgeBase as a *cognitive infrastructure* — an environment that not only executes code, but also understands, measures, and explains its own operation.

> *"The ForgeBase core is the body where ForgeProcess thought manifests and self-evaluates."*

---

## 1. Project Objectives

### Main Objectives

* Establish **a consistent Clean + Hexagonal architecture** across all modules.
* Standardize the **folder structure and imports** to reduce coupling and ambiguity.
* Ensure **native testability and observability** at all levels of the system.
* Provide a solid foundation for cognitive extensions (CLI, API, LLM, AI agents).
* Enable continuous evolution without loss of architectural coherence.

### Initial Scope

* Modularization of the `forge_base/` directory (core).
* Definition of base classes (`EntityBase`, `UseCaseBase`, `PortBase`, `AdapterBase`).
* Implementation of modular import conventions.
* Introduction of `observability/` and `testing/` modules as first-class components.

---

## 2. Architectural Philosophy

ForgeBase must reflect the cognitive principles of the Forge Framework:

1. **Reflexivity:** the system must understand and measure its own operations.
2. **Autonomy:** the domain must remain isolated from infrastructure.
3. **Extensibility:** any new functionality must be added via adapters and ports, without modifying the core.
4. **Traceability:** every execution must be auditable and linked to the intent that originated it.
5. **Cognitive Consistency:** code and documentation are mirrors of each other.

---

## 3. Proposed Modular Structure

Below is the reference structure for the ForgeBase core:

```
forge_base/
├─ __init__.py
│
├─ domain/                          # Entity and invariant core
│  ├─ __init__.py
│  ├─ entity_base.py                # Base class for entities
│  ├─ value_object_base.py          # Immutable domain objects
│  ├─ exceptions.py                 # Domain errors and exceptions
│  └─ validators/                   # Rules and invariants
│     ├─ __init__.py
│     └─ rules.py
│
├─ application/                     # Use cases and cognitive orchestration
│  ├─ __init__.py
│  ├─ usecase_base.py               # Base class for UseCases
│  ├─ port_base.py                  # Base class for Ports (cognitive contracts)
│  ├─ dto_base.py                   # Standardized DTOs
│  ├─ error_handling.py             # Guards and exception handling
│  └─ decorators/                   # Decorators for metrics and feedback
│     ├─ __init__.py
│     └─ track_metrics.py
│
├─ adapters/                        # External interfaces and connectors
│  ├─ __init__.py
│  ├─ adapter_base.py               # Base class for Adapters
│  ├─ cli/                          # CLI interface
│  │  ├─ __init__.py
│  │  └─ cli_adapter.py
│  ├─ http/                         # REST / HTTP interface
│  │  ├─ __init__.py
│  │  └─ http_adapter.py
│  └─ ai/                           # Cognitive adapters (LLM, agents)
│     ├─ __init__.py
│     └─ llm_adapter.py
│
├─ infrastructure/                  # Technical services and persistence
│  ├─ __init__.py
│  ├─ repository/                   # Persistence and storage
│  │  ├─ __init__.py
│  │  ├─ repository_base.py
│  │  ├─ json_repository.py
│  │  └─ sql_repository.py
│  ├─ logging/                      # Structured logging and tracing
│  │  ├─ __init__.py
│  │  └─ logger_port.py
│  ├─ configuration/                # Settings and loading
│  │  ├─ __init__.py
│  │  └─ config_loader.py
│  └─ security/                     # Sandbox and authentication
│     ├─ __init__.py
│     └─ sandbox.py
│
├─ observability/                   # Feedback and metrics core
│  ├─ __init__.py
│  ├─ log_service.py                # Structured logging service
│  ├─ track_metrics.py              # Metrics and telemetry
│  ├─ tracer_port.py                # Distributed tracing interface
│  └─ feedback_manager.py           # Process <-> Base integration
│
├─ testing/                         # Cognitive testing framework
│  ├─ __init__.py
│  ├─ forge_test_case.py            # Base class for tests
│  ├─ fakes/                        # Fake implementations for simulations
│  │  ├─ __init__.py
│  │  └─ fake_logger.py
│  └─ fixtures/                     # Simulated data for regression
│     ├─ __init__.py
│     └─ sample_data.py
│
└─ core_init.py                     # Cognitive initialization and bootstrap
```

---

## 4. Fundamental Classes

### `EntityBase`

* Represents domain entities.
* Maintains invariants and local rules.
* Must be completely independent from infrastructure.

```python
class EntityBase:
    def __init__(self):
        self._id = None
```

### `UseCaseBase`

* Defines the contract for use cases (ValueTracks).
* Must contain the orchestration and integration logic between domain and adapters.

```python
class UseCaseBase:
    def execute(self, *args, **kwargs):
        raise NotImplementedError
```

### `PortBase`

* Abstract interface for communication between internal and external modules.
* Ensures traceability and contract documentation.

```python
class PortBase:
    def info(self):
        return {"port": self.__class__.__name__, "module": self.__module__}
```

### `AdapterBase`

* Implements port contracts and adds feedback instrumentation.

```python
class AdapterBase:
    def __init__(self):
        self.name = self.__class__.__name__
```

---

## 5. Implementation Conventions

1. **Organized imports**
   Always use clear modular syntax:

   ```python
   from forge_base.domain import EntityBase
   from forge_base.application import UseCaseBase, PortBase
   from forge_base.adapters import AdapterBase
   ```

2. **Absolute domain isolation**
   No module outside of `domain/` should modify entities or internal rules.

3. **Standard observability**
   Every UseCase, Port, and Adapter must emit metrics automatically through the `track_metrics` decorator.

4. **Feedback as a contract**
   Every relevant execution must generate technical and semantic feedback (logs, metrics, handled exceptions).

5. **Cognitive tests**
   Tests must document the technical reasoning and cover intent cases, not just execution cases.

---

## 6. Technical Requirements

* Compatibility with Python 3.11+.
* Standardized docstrings in reST format.
* Instrumentation via `forgecore.observability`.
* Independent modular execution (each module must be testable in isolation).
* YAML <-> Code mapping (Process <-> Base synchronization).

---

## 7. Success Criteria

| Category          | Indicator              | Target                                                       |
| ----------------- | ---------------------- | ------------------------------------------------------------ |
| **Modularization** | Unified imports        | 100% of modules compatible with `from forge_base.[module]`   |
| **Testability**    | Test coverage          | >= 90% of the core                                           |
| **Observability**  | Automatic metrics      | 100% of UseCases and Ports instrumented                      |
| **Decoupling**     | Cross-dependencies     | 0 prohibited dependencies between layers                    |
| **Evolvability**   | Adding new Adapters    | No modifications required in the core                        |

---

## 8. Implementation Roadmap

| Phase                    | Deliverables                 | Description                                                            |
| ------------------------ | ---------------------------- | ---------------------------------------------------------------------- |
| **1. Planning**          | Directory structure          | Define folders and base classes                                        |
| **2. Implementation**    | Base classes + Imports       | Create and validate `EntityBase`, `UseCaseBase`, `PortBase`, `AdapterBase` |
| **3. Observability**     | Active `observability` module | Integrate metrics, logs, and tracing                                   |
| **4. Testability**       | Validated core               | Create automated cognitive tests                                       |
| **5. Synchronization**   | ForgeProcess <-> ForgeBase   | Enable artifact sync via YAML                                          |

---

## Conclusion

The modularization of the ForgeBase core represents the definitive step toward the architectural maturity of the Forge Framework.
It consolidates ForgeBase as a **reflexive, modular, and observable** infrastructure, ready to operate as the central environment for the Forge's cognitive intelligence.

> *"The ForgeBase code is the body of a mind that thinks in software."*
