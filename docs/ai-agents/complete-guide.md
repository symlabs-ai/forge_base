# ForgeBase - Complete Guide for AI Agents

> Full reference for ForgeBase programmatic APIs for AI code agents.

## Overview

ForgeBase provides programmatic Python APIs designed specifically for AI code agents. Instead of parsing CLI text output, AI agents can import Python classes that return structured data (dataclasses, dicts) suitable for programmatic analysis.

## Why This Matters

### Old Method (CLI)
```python
import subprocess

# AI has to parse text output
result = subprocess.run(["python", "devtool.py", "lint"], capture_output=True)
output = result.stdout  # "Ruff check passed"

# AI has to use regex/parse unstructured text
if "passed" in output:
    # Hope the format doesn't change...
```

### New Method (API)
```python
from forge_base.dev.api import QualityChecker

# AI gets structured data
checker = QualityChecker()
result = checker.run_ruff()

# AI can reason about specific errors
if not result.passed:
    for error in result.errors:
        if error['code'] == 'F401':  # Unused import
            remove_import(error['file'], error['line'])
```

---

## Available APIs

### 1. QualityChecker

**Purpose**: Code quality validation (linting, type checking, architecture)

**Returns**: `CheckResult` with structured errors

```python
from forge_base.dev.api import QualityChecker

checker = QualityChecker()

# Run individual checks
ruff_result = checker.run_ruff()
mypy_result = checker.run_mypy()
arch_result = checker.run_import_linter()
deps_result = checker.run_deptry()

# Run all checks
results = checker.run_all()

# Analyze results
for tool, result in results.items():
    if not result.passed:
        print(f"{tool}: {result.error_count} errors")
        for error in result.errors:
            # AI can act on specific error codes
            fix_error(error)
```

**CheckResult Structure**:
```python
@dataclass
class CheckResult:
    tool: str                # "ruff", "mypy", etc.
    passed: bool             # True if no errors
    errors: list[dict]       # Structured errors with file, line, message, code
    warnings: list[dict]     # Non-blocking warnings
    suggestions: list[str]   # AI-actionable suggestions
    duration: float          # Execution time
    exit_code: int
    raw_output: str          # For debugging
```

**Error Structure** (Ruff example):
```python
{
    "file": "user.py",
    "line": 42,
    "column": 10,
    "message": "Unused import: `sys`",
    "code": "F401",
    "severity": "error"
}
```

---

### 2. ScaffoldGenerator

**Purpose**: Generate boilerplate code

**Returns**: `ScaffoldResult` with generated code as a string

```python
from forge_base.dev.api import ScaffoldGenerator

generator = ScaffoldGenerator()

# Generate a UseCase
result = generator.create_usecase(
    name="CreateOrder",
    input_type="CreateOrderInput",
    output_type="CreateOrderOutput",
    repository="OrderRepositoryPort"
)

if result.success:
    # AI can modify code before writing
    code = result.code
    code = customize_for_context(code)

    # Write to the suggested path
    write_file(result.file_path, code)

# Generate an Entity
result = generator.create_entity(
    name="Order",
    attributes=["customer_id", "total", "items"]
)
```

**ScaffoldResult Structure**:
```python
@dataclass
class ScaffoldResult:
    component_type: str      # "usecase", "entity", etc.
    name: str                # Component name
    code: str                # Generated code
    file_path: str           # Suggested file path
    success: bool
    error: str
    metadata: dict           # Imports, dependencies, etc.
```

---

### 3. ComponentDiscovery

**Purpose**: Scan the codebase and catalog components

**Returns**: `DiscoveryResult` with all found components

```python
from forge_base.dev.api import ComponentDiscovery

discovery = ComponentDiscovery()
result = discovery.scan_project()

# AI analyzes architecture
print(f"Entities: {len(result.entities)}")
print(f"UseCases: {len(result.usecases)}")
print(f"Repositories: {len(result.repositories)}")

# AI makes recommendations
if len(result.usecases) < len(result.entities):
    print("Consider creating more UseCases")

# AI finds unused components
for entity in result.entities:
    if not any(entity.name in uc.imports for uc in result.usecases):
        print(f"{entity.name} not used in any UseCase")
```

**DiscoveryResult Structure**:
```python
@dataclass
class DiscoveryResult:
    entities: list[ComponentInfo]
    usecases: list[ComponentInfo]
    repositories: list[ComponentInfo]
    ports: list[ComponentInfo]
    value_objects: list[ComponentInfo]
    adapters: list[ComponentInfo]
    total_files_scanned: int
    scan_duration: float
```

**ComponentInfo Structure**:
```python
@dataclass
class ComponentInfo:
    name: str
    type: str                # 'entity', 'usecase', etc.
    file_path: str
    line_number: int
    base_class: str
    imports: list[str]
    docstring: str
```

---

### 4. TestRunner

**Purpose**: Run tests with structured results

**Returns**: `TestResult` with detailed test information

```python
from forge_base.dev.api import TestRunner

runner = TestRunner()

# Run specific test types
unit_result = runner.run_unit_tests()
integration_result = runner.run_integration_tests()
property_result = runner.run_property_tests()
contract_result = runner.run_contract_tests()

# Run all tests
results = runner.run_all()

# AI analyzes failures
for test_type, result in results.items():
    if not result.passed:
        for failure in result.failures:
            # AI can reason about failure types
            if "AssertionError" in failure.error_type:
                fix_assertion(failure.file, failure.line)
            elif "TypeError" in failure.error_type:
                add_type_hints(failure.file, failure.line)
```

**TestResult Structure**:
```python
@dataclass
class TestResult:
    test_type: str           # "unit", "integration", etc.
    passed: bool
    total: int
    passed_count: int
    failed_count: int
    skipped_count: int
    failures: list[TestFailure]
    duration: float
    coverage: float
    exit_code: int
    raw_output: str
```

**TestFailure Structure**:
```python
@dataclass
class TestFailure:
    test_name: str
    file: str
    line: int
    message: str
    traceback: str
    error_type: str          # "AssertionError", "TypeError", etc.
```

---

## Complete AI Agent Workflow Example

```python
from forge_base.dev.api import (
    QualityChecker,
    ComponentDiscovery,
    TestRunner,
    ScaffoldGenerator
)

def ai_agent_workflow():
    """Complete AI agent workflow."""

    # 1. Analyze current codebase
    discovery = ComponentDiscovery()
    components = discovery.scan_project()

    if len(components.usecases) < 5:
        # 2. Generate missing component
        generator = ScaffoldGenerator()
        result = generator.create_usecase("UpdateOrder")

        # 3. Customize generated code
        code = result.code
        code = add_custom_logic(code)
        write_file(result.file_path, code)

    # 4. Check quality
    checker = QualityChecker()
    quality_results = checker.run_all()

    # 5. Fix issues
    for tool, result in quality_results.items():
        if not result.passed:
            for error in result.errors:
                auto_fix_error(error)

    # 6. Run tests
    runner = TestRunner()
    test_results = runner.run_all()

    # 7. Fix failing tests
    for test_type, result in test_results.items():
        if not result.passed:
            for failure in result.failures:
                fix_test(failure)

    # 8. Verify everything passes
    final_quality = checker.run_all()
    final_tests = runner.run_all()

    all_passed = (
        all(r.passed for r in final_quality.values()) and
        all(r.passed for r in final_tests.values())
    )

    if all_passed:
        # 9. Ready to commit
        create_commit("feat: AI-generated code with full validation")
```

---

## Data Structures Summary

All APIs return **dataclasses** that can be:
- Converted to dict: `result.to_dict()`
- Serialized to JSON
- Analyzed programmatically
- Used for AI decision-making

No unstructured text parsing needed!

---

## Getting Started

### Installation
```bash
pip install -e ".[dev]"
```

### Basic Usage
```python
# Import APIs
from forge_base.dev.api import (
    QualityChecker,
    ScaffoldGenerator,
    ComponentDiscovery,
    TestRunner,
)

# Use directly
checker = QualityChecker()
results = checker.run_all()

# AI makes decisions based on structured data
if not all(r.passed for r in results.values()):
    fix_quality_issues(results)
```

### Advanced Usage
See `examples/ai_agent_usage.py` for comprehensive examples.

---

## CLI Still Available

The `devtool.py` CLI is still available for:
- Human developers
- Shell scripts
- CI/CD pipelines
- Backward compatibility

But AI agents should use the Python APIs for:
- Structured data
- No subprocess overhead
- Better error handling
- Programmatic analysis

---

## API Reference

For full API documentation, see:
- `forge_base/dev/api/quality.py` - QualityChecker
- `forge_base/dev/api/scaffold.py` - ScaffoldGenerator
- `forge_base/dev/api/discovery.py` - ComponentDiscovery
- `forge_base/dev/api/testing.py` - TestRunner

All classes have comprehensive docstrings with type hints.

---

## Best Practices for AI Agents

### 1. Always Check Success
```python
result = generator.create_usecase("CreateOrder")
if not result.success:
    handle_error(result.error)
```

### 2. Use Structured Errors
```python
for error in result.errors:
    # Don't: parse error message strings
    # Do: use error['code'], error['file'], error['line']
    if error['code'] == 'F401':
        remove_unused_import(error['file'], error['line'])
```

### 3. Leverage Suggestions
```python
for suggestion in result.suggestions:
    # AI can execute suggestions
    execute_suggestion(suggestion)
```

### 4. Convert to Dict for Serialization
```python
result_dict = result.to_dict()
save_to_file("analysis.json", json.dumps(result_dict))
```

### 5. Iterate and Validate
```python
# Generate -> Check -> Fix -> Repeat
while not all_quality_checks_passed():
    fix_next_issue()
    recheck()
```

---

## Integration with Claude Code

Claude Code (and other AI assistants) can use these APIs directly:

```python
# Claude Code can do this:
from forge_base.dev.api import QualityChecker

checker = QualityChecker()
result = checker.run_ruff()

# Claude analyzes structured data
for error in result.errors:
    # Claude knows exactly what to fix
    fix_code(error['file'], error['line'], error['code'])
```

No more parsing text output or guessing formats!

---

## Project Configuration

### File Types to Create

| Type | Location | Base |
|------|----------|------|
| Entity | `src/domain/` | `EntityBase` |
| ValueObject | `src/domain/` | `ValueObjectBase` |
| UseCase | `src/application/` | `UseCaseBase` |
| Port | `src/application/` | `PortBase` |
| Adapter | `src/adapters/` | `AdapterBase` |
| Repository | `src/infrastructure/` | `RepositoryBase` |

### Naming Conventions

| Component | Pattern |
|-----------|---------|
| Entity | `NameEntity` or just `Name` |
| UseCase | `VerbNameUseCase` (e.g., `CreateOrderUseCase`) |
| Port | `NamePort` (e.g., `OrderRepositoryPort`) |
| Adapter | `NameAdapter` (e.g., `EmailNotificationAdapter`) |
| DTO Input | `VerbNameInput` (e.g., `CreateOrderInput`) |
| DTO Output | `VerbNameOutput` (e.g., `CreateOrderOutput`) |

---

## Error Handling

### Common Error Codes

| Code | Source | Action |
|------|--------|--------|
| `F401` | Ruff | Remove unused import |
| `F841` | Ruff | Remove unused variable |
| `E501` | Ruff | Break long line |
| `no-untyped-def` | Mypy | Add type hints |
| `import-error` | Mypy | Check dependencies |
| `DEP001` | Deptry | Add missing dependency |
| `DEP002` | Deptry | Remove unused dependency |

### Auto-Fix Example

```python
def auto_fix_error(error: dict) -> None:
    """Automatically fix an error based on its code."""
    code = error.get("code", "")
    file = error.get("file", "")
    line = error.get("line", 0)

    if code == "F401":
        # Remove the line with unused import
        remove_line(file, line)

    elif code == "E501":
        # Reformat the long line
        reformat_long_line(file, line)

    elif code == "no-untyped-def":
        # Add type hints
        add_type_hints(file, line)
```

---

**Version**: ForgeBase 0.1.4
**For**: AI Code Agents
