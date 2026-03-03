# Contributing to ForgeBase

> "To forge is to transform thought into structure — together."

Thank you for your interest in contributing to ForgeBase! This document guides you on how to contribute effectively and in alignment with the project's principles.

---

## Code of Conduct

ForgeBase adopts the principles of **Reflexivity**, **Autonomy**, and **Cognitive Coherence**. We expect contributors to:

- Be respectful and constructive in discussions
- Value clear and explanatory code
- Prioritize architecture over quick fixes
- Document decisions (not just code)
- Test not only behavior, but intent

---

## How to Contribute

### 1. Reporting Bugs

**Before Reporting:**
- Check if the bug has already been reported in [Issues](https://github.com/symlabs-ai/forge_base/issues)
- Confirm it is a bug (not expected behavior)
- Try to reproduce in a clean environment

**Creating a Bug Report:**

```markdown
**Bug Description:**
[Clear description of the problem]

**How to Reproduce:**
1. Create entity X with property Y
2. Execute method Z
3. Observe error

**Expected Behavior:**
[What should happen]

**Actual Behavior:**
[What is happening]

**Environment:**
- ForgeBase version: 1.0.0
- Python version: 3.11.0
- OS: Ubuntu 22.04

**Stacktrace:**
```
[Paste the full stack trace]
```

**Code to Reproduce:**
```python
# Minimal code that reproduces the bug
```
```

### 2. Suggesting Features

**Before Suggesting:**
- Check if the feature has already been suggested
- Consider whether it aligns with ForgeBase philosophy (Clean Architecture, Observability First, etc.)
- Think of alternatives

**Creating a Feature Request:**

```markdown
**Problem it Solves:**
[What problem does this feature solve?]

**Proposed Solution:**
[How you envision it working]

**Alternatives Considered:**
[Other ways to solve the problem]

**Architecture Impact:**
[How it affects Clean Architecture, Ports/Adapters, etc.]

**Usage Example:**
```python
# How the feature would be used
```
```

### 3. Contributing Code

#### Setting Up the Environment

```bash
# Clone the repository
git clone https://github.com/symlabs-ai/forge_base.git
cd forge_base

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

#### Development Workflow

1. **Create a Branch**

```bash
git checkout -b feature/my-feature
# or
git checkout -b fix/my-bugfix
```

Naming conventions:
- `feature/` — New functionality
- `fix/` — Bug fix
- `docs/` — Documentation only
- `refactor/` — Refactoring without behavior change
- `test/` — Adding/improving tests

2. **Write Code (TDD)**

```bash
# 1. Write the test first
vim tests/unit/domain/test_my_feature.py

# 2. Run tests (should fail)
pytest tests/unit/domain/test_my_feature.py

# 3. Implement the feature
vim src/forge_base/domain/my_feature.py

# 4. Run tests (should pass)
pytest tests/unit/domain/test_my_feature.py

# 5. Refactor
# ...

# 6. Run the full suite
pytest
```

3. **Write reST Docstrings**

```python
def my_function(param: str, value: int) -> bool:
    """
    [One line describing what it does]

    [Paragraph explaining WHY this implementation,
    design decisions, and architectural context]

    :param param: Description of param
    :type param: str
    :param value: Description of value
    :type value: int
    :return: Description of return value
    :rtype: bool
    :raises ValueError: When value is negative

    Example::

        >>> result = my_function("test", 42)
        >>> print(result)
        True

    See Also:
        - :class:`RelatedClass`
        - :func:`related_function`
    """
    pass
```

4. **Run Linting**

```bash
# Ruff linting + formatting
ruff check .
ruff format .

# Type checking
mypy src/forge_base
```

5. **Run Full Tests**

```bash
# All tests
pytest

# With coverage
pytest --cov=forge_base --cov-report=html

# Specific tests
pytest tests/unit/domain/

# Only fast tests
pytest -m "not slow"
```

6. **Commit with Conventional Message**

```bash
git add .
git commit -m "feat: add MongoDB Repository support

Implements MongoDBRepository extending RepositoryBase
to enable persistence in MongoDB.

- Adds MongoDBRepository in infrastructure/repository/
- Adds tests in tests/unit/infrastructure/
- Updates cookbook documentation

Refs #123
"
```

**Commit Format:**

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Formatting (no code change)
- `refactor`: Refactoring without behavior change
- `test`: Adding/changing tests
- `chore`: Maintenance tasks

**Examples:**

```bash
feat(domain): add Money ValueObject
fix(repository): fix race condition in save()
docs(adr): add ADR-007 on caching
refactor(usecase): simplify input validation
test(integration): add YAML sync tests
```

7. **Push and Open Pull Request**

```bash
git push origin feature/my-feature
```

On GitHub:
- Open a Pull Request
- Fill in the template (description, tests, screenshots if applicable)
- Wait for code review

---

## Pull Request Checklist

Before submitting, verify:

### Code

- [ ] Code follows Clean Architecture (correct dependencies)
- [ ] Ports and Adapters clearly separated
- [ ] Complete type hints
- [ ] No commented-out code (remove or document why)
- [ ] No print() statements (use logger)
- [ ] No circular dependencies

### Tests

- [ ] Unit tests written (>=90% coverage for new code)
- [ ] Tests pass locally (`pytest`)
- [ ] Cognitive tests if applicable (ForgeTestCase)
- [ ] Does not break existing tests

### Documentation

- [ ] reST docstrings on all public classes/methods
- [ ] Docstrings explain "why", not just "what"
- [ ] Usage examples included
- [ ] README updated if necessary
- [ ] CHANGELOG.md updated (Unreleased section)

### Observability

- [ ] Structured logging added if applicable
- [ ] Metrics collected if applicable
- [ ] Appropriate error handling

### Architectural Decisions

- [ ] ADR created if significant decision
- [ ] Considered alternatives documented

---

## Testing Patterns

### Test Structure

```
tests/
├── unit/                    # Unit tests (isolated)
│   ├── domain/
│   │   ├── test_entity.py
│   │   └── test_value_object.py
│   ├── application/
│   │   └── test_usecase.py
│   └── infrastructure/
│       └── test_repository.py
├── integration/             # Integration tests
│   ├── test_yaml_sync.py
│   └── test_sql_repository.py
└── cognitive/              # Cognitive tests
    └── test_create_user_cognitive.py
```

### Unit Test Example

```python
import unittest
from forge_base.domain import ValidationError


class TestUser(unittest.TestCase):
    """Unit tests for User entity."""

    def test_creates_user_with_valid_data(self):
        """Test user creation with valid data."""
        user = User(name="Alice", email="alice@example.com")

        self.assertEqual(user.name, "Alice")
        self.assertEqual(user.email, "alice@example.com")
        self.assertTrue(user.is_active)

    def test_rejects_empty_name(self):
        """Test that empty name is rejected."""
        with self.assertRaises(ValidationError) as ctx:
            User(name="", email="alice@example.com")

        self.assertIn("name cannot be empty", str(ctx.exception).lower())

    def test_validates_email_format(self):
        """Test email format validation."""
        with self.assertRaises(ValidationError):
            User(name="Alice", email="invalid-email")
```

### Cognitive Test Example

```python
from forge_base.testing import ForgeTestCase
from forge_base.testing.fakes import FakeRepository, FakeLogger


class TestCreateUserCognitive(ForgeTestCase):
    """Cognitive tests for CreateUser UseCase."""

    def test_creates_user_with_intent_validation(self):
        """Cognitive test validating intent, metrics, and performance."""
        # Setup
        fake_repo = FakeRepository()
        fake_logger = FakeLogger()
        usecase = CreateUserUseCase(
            user_repository=fake_repo,
            logger=fake_logger
        )

        # Intent
        intent = "Create user Alice with email alice@example.com"

        # Execute
        output = usecase.execute(CreateUserInput(
            name="Alice",
            email="alice@example.com"
        ))

        # Cognitive validations
        actual = f"Created user {output.name} with email {output.email}"
        self.assert_intent_matches(intent, actual, threshold=0.80)

        # Metrics validation
        self.assert_metrics_collected({
            'create_user.count': lambda v: v == 1
        })

        # Performance validation
        self.assert_performance_within(
            lambda: usecase.execute(CreateUserInput(...)),
            max_duration_ms=50.0
        )
```

---

## Code Patterns

### Clean Architecture

**Dependency Rules:**

```python
# OK: Application -> Domain
from forge_base.domain import EntityBase

class CreateUserUseCase(UseCaseBase):
    pass

# OK: Infrastructure -> Application
from forge_base.application import PortBase

class JSONRepository(PortBase):
    pass

# WRONG: Domain -> Application
from forge_base.application import UseCaseBase  # NO!

class User(EntityBase):
    pass

# WRONG: Domain -> Infrastructure
from forge_base.infrastructure import JSONRepository  # NO!

class User(EntityBase):
    pass
```

### Dependency Injection

**Always use constructor injection:**

```python
# Correct
class CreateUserUseCase(UseCaseBase):
    def __init__(
        self,
        user_repository: UserRepositoryPort,  # Port, not adapter
        logger: LoggerPort
    ):
        self.user_repository = user_repository
        self.logger = logger

# Wrong
class CreateUserUseCase(UseCaseBase):
    def __init__(self):
        self.user_repository = JSONRepository()  # Direct coupling
        self.logger = StdoutLogger()
```

### Naming Conventions

```python
# Entities: Nouns (singular)
class User(EntityBase): pass
class Order(EntityBase): pass

# ValueObjects: Compound nouns
class EmailAddress(ValueObjectBase): pass
class Money(ValueObjectBase): pass

# UseCases: Verb + Noun + "UseCase"
class CreateUserUseCase(UseCaseBase): pass
class PlaceOrderUseCase(UseCaseBase): pass

# Ports: Noun + "Port"
class UserRepositoryPort(ABC): pass
class NotificationServicePort(ABC): pass

# Adapters: Technology + Noun + "Adapter"
class JSONUserRepository(UserRepositoryPort): pass
class SMTPNotificationAdapter(NotificationServicePort): pass
class HTTPAdapter(AdapterBase): pass

# DTOs: UseCase + "Input"/"Output"
class CreateUserInput(DTOBase): pass
class CreateUserOutput(DTOBase): pass
```

### Error Handling

```python
# Domain errors
from forge_base.domain import ValidationError, BusinessRuleViolation

# ValidationError: Invalid data
if not email:
    raise ValidationError("Email cannot be empty")

# BusinessRuleViolation: Business rule violated
if user_exists:
    raise BusinessRuleViolation(f"User with email {email} already exists")

# Application errors
from forge_base.application import UseCaseError

# UseCaseError: Orchestration error
if customer is None:
    raise UseCaseError(f"Customer not found: {customer_id}")
```

---

## Documentation

### ADRs (Architecture Decision Records)

For significant architectural decisions, create an ADR:

```bash
# Create ADR
vim docs/adr/007-my-decision.md
```

**Template:**

```markdown
# ADR-007: [Decision Title]

## Status

**Proposed** | **Accepted** | **Superseded**

## Context

[Context and problem that motivated the decision]

## Decision

[Decision made]

## Consequences

### Positive
- Benefit 1
- Benefit 2

### Negative
- Trade-off 1
- Trade-off 2

## Alternatives Considered

### Alternative 1
[Why it was rejected]

### Alternative 2
[Why it was rejected]

## References

- Link 1
- Link 2
```

---

## Review Process

### For Reviewers

**What to evaluate:**

1. **Architecture**
   - Clean Architecture respected?
   - Correct dependencies?
   - Appropriate Ports/Adapters?

2. **Code**
   - Readability and clarity
   - Complete type hints
   - No code smells

3. **Tests**
   - Adequate coverage
   - Tests pass
   - Edge cases covered

4. **Documentation**
   - Docstrings present and complete
   - Clear examples
   - ADR if necessary

**How to give feedback:**

```markdown
# Good feedback (constructive)
"Great implementation! I suggest extracting this validation into a reusable validator, as it could be useful elsewhere. Example: `DomainValidators.validate_email()`"

# Bad feedback (not constructive)
"This is wrong."
```

### For Authors

**Responding to feedback:**

- Be receptive
- Ask if you don't understand
- Don't take it personally
- Thank the reviewer for their time

**Iterating:**

```bash
# Make requested changes
vim src/forge_base/domain/my_feature.py

# Commit with PR reference
git commit -m "fix: correct validation per review feedback

Ref #45 (comment)
"

# Push update
git push origin feature/my-feature
```

---

## Resources for Contributors

### Documentation

- **[Getting Started](docs/getting-started.md)** — Getting started tutorial
- **[Cookbook](docs/cookbook.md)** — Practical recipes
- **[ADRs](docs/adr/)** — Architectural decisions
- **[Testing Guide](docs/testing-guide.md)** — How to test

### Examples

- `examples/complete_flow.py` — Complete example
- `examples/user_management/` — Sample app

### Recommended Reading

- **Clean Architecture** by Robert C. Martin
- **Domain-Driven Design** by Eric Evans
- **Hexagonal Architecture** by Alistair Cockburn
- **Growing Object-Oriented Software, Guided by Tests** by Freeman & Pryce

---

## Reporting Security Issues

**DO NOT** open a public issue for security problems.

Send an email to: security@forgebase.dev

Include:
- Vulnerability description
- Steps to reproduce
- Potential impact
- Fix suggestion (if available)

---

## Community

- **GitHub Discussions:** For questions and discussions
- **GitHub Issues:** For bugs and features
- **Pull Requests:** For code contributions

---

## FAQ

**Q: Can I contribute if I'm not an expert in Clean Architecture?**
A: Yes! Read the ADRs and examples. We provide help during review.

**Q: My PR was rejected. Now what?**
A: Read the feedback, ask if you don't understand, and iterate. Not every PR is accepted on the first attempt.

**Q: Can I contribute with documentation only?**
A: Absolutely! Docs are as important as code.

**Q: How do I know if a feature will be accepted?**
A: Open a discussion issue before implementing. We can validate alignment with the roadmap.

**Q: Can I use library X in my PR?**
A: We prefer zero external dependencies. If absolutely necessary, justify it in the discussion.

---

## License

By contributing to ForgeBase, you agree that your contributions will be licensed under the same project license (MIT License).

---

**Thank you for contributing!**

*"Each contribution forges the framework's future."*
