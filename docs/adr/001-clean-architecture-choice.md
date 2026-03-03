# ADR-001: Clean Architecture Choice

## Status

**Accepted** (2025-11-03)

## Context

ForgeBase was conceived as the technical core of the Forge Framework, responsible for executing business logic defined by ForgeProcess. We needed an architecture that:

- Isolated domain logic from technical details (UI, database, frameworks)
- Enabled maximum testability without external dependencies
- Facilitated maintenance and evolution over time
- Ensured that business decisions were not contaminated by technical concerns
- Allowed swapping infrastructure implementations without affecting the core

### Forces at Play

**Positive:**
- Need for clear separation of responsibilities
- Requirement for testability independent of infrastructure
- Expectation of frequent changes in adapters (CLI, HTTP, AI)
- Desire for the domain to be "pure" and expressive

**Negative:**
- Potential overhead of creating too many layers
- Learning curve for new developers
- Need for discipline to maintain boundaries

## Decision

**We adopted Clean Architecture as the architectural standard for ForgeBase.**

The implementation follows 4 concentric layers:

```
┌─────────────────────────────────────────────┐
│           Adapters (External)               │  ← CLI, HTTP, AI
│  ┌───────────────────────────────────────┐  │
│  │     Application (Use Cases)           │  │  ← Orchestration
│  │  ┌─────────────────────────────────┐  │  │
│  │  │      Domain (Entities, VOs)     │  │  │  ← Business rules
│  │  └─────────────────────────────────┘  │  │
│  └───────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
```

### Dependency Rules

1. **Domain** depends on nothing (zero imports outside the domain)
2. **Application** depends only on Domain
3. **Adapters** can depend on Application and Domain
4. **Infrastructure** implements contracts defined by Application/Domain

### Implementation in ForgeBase

```python
# Domain Layer (src/forge_base/domain/)
- EntityBase: Entities with identity
- ValueObjectBase: Immutable value objects
- Exceptions: ValidationError, BusinessRuleViolation
- Validators: Reusable rules

# Application Layer (src/forge_base/application/)
- UseCaseBase: Logic orchestration
- PortBase: Communication contracts
- DTOBase: Data Transfer Objects

# Infrastructure Layer (src/forge_base/infrastructure/)
- RepositoryBase: Persistence
- ConfigLoader: Configuration
- LoggerPort: Logging

# Adapters Layer (src/forge_base/adapters/)
- CLIAdapter: Command-line interface
- HTTPAdapter: REST API
```

### Enforcement

We use tests to ensure boundaries:
- Import tests validate zero circular dependencies
- Code review checks for violations
- Linting rules detect forbidden imports

## Consequences

### Positive

✅ **Maximum Testability**
- Domain testable without mocks (pure logic)
- Application testable with simple fakes
- Adapters testable with mocked ports

✅ **Infrastructure Flexibility**
- Switch from JSON to SQL without affecting UseCases
- Add a new adapter (gRPC, GraphQL) without modifying the core
- Migrate from CLI to HTTP without rewriting logic

✅ **Clear Separation of Concerns**
- Business rules expressed in ubiquitous language
- Technical details isolated in adapters
- Explicit orchestration in UseCases

✅ **Maintainability**
- Changes localized to a single layer
- Independent evolution of each layer
- Code easier to understand and navigate

### Negative

⚠️ **Initial Overhead**
- More files and abstractions
- More complex initial setup
- Need to understand the pattern

⚠️ **Discipline Required**
- Developers must respect boundaries
- Temptation to take "shortcuts" violating layers
- Critical code review to maintain the pattern

⚠️ **Boilerplate**
- DTOs for input/output
- Ports for each external dependency
- Mapping between layers

### Mitigations

To minimize negative consequences:

1. **Clear Documentation**: ADRs, guides, examples
2. **Code Generators**: Automatic UseCase scaffolding
3. **Linting**: Automatic violation detection
4. **Examples**: Complete flow examples showing the pattern
5. **Testing Utilities**: Pre-built fakes to speed up tests

## Alternatives Considered

### 1. MVC/MTV (Model-View-Controller)

**Rejected because:**
- Mixes presentation concerns with business logic
- Models frequently contaminated with ORM details
- Hard to test controllers without a web framework
- Does not clearly express domain rules

### 2. Traditional Layered Architecture

**Rejected because:**
- Allows bidirectional dependencies between layers
- Domain frequently coupled to infrastructure
- Hard to avoid "leaky abstractions"
- Does not enforce domain isolation

### 3. Microservices from the Start

**Rejected because:**
- Unnecessary operational overhead at the beginning
- Complexity of inter-service communication
- Clean Architecture allows migrating to microservices later
- ForgeBase is a framework, not a distributed application

### 4. Flat Architecture (no layers)

**Rejected because:**
- Tendency to create a "big ball of mud"
- Hard to maintain separation of concerns
- Tests coupled to infrastructure
- Chaotic evolution over time

## References

- **Clean Architecture** by Robert C. Martin (Uncle Bob)
- **Domain-Driven Design** by Eric Evans
- **Hexagonal Architecture** by Alistair Cockburn
- **ForgeBase PRD**: `/docs/guides/forgebase_PRD.md`
- **ForgeBase Guide**: `/docs/guides/forgebase_guide.md`

## Related ADRs

- [ADR-002: Hexagonal Ports & Adapters](002-hexagonal-ports-adapters.md) — Complements with the Ports/Adapters pattern
- [ADR-005: Dependency Injection](005-dependency-injection.md) — DI implementation respecting Clean Architecture

---

**Author:** ForgeBase Development Team
**Date:** 2025-11-03
**Version:** 1.0
