# ForgeBase AI Agent Quick Start Guide

**Target Audience**: AI Coding Agents (Claude Code, Cursor, GitHub Copilot, Aider, etc.)

## 🚀 Quick Reference

### Import Everything You Need

```python
from forgebase.dev.api import (
    QualityChecker,
    ScaffoldGenerator,
    ComponentDiscovery,
    TestRunner
)
```

### 📚 Access This Guide Programmatically

```python
# AI agents can load this guide programmatically (even after pip install)
from forgebase.dev import get_agent_quickstart

guide = get_agent_quickstart()
print(guide)  # Full markdown content of this file
```

**Why this matters for AI agents:**
- ✅ Works even when installed via `pip install git+...`
- ✅ No internet required
- ✅ Always in sync with installed version
- ✅ Can be parsed for API discovery

## 📊 API 1: Quality Checking (Replace CLI quality checks)

**When to use**: Before commits, during code review, fixing linting errors

```python
checker = QualityChecker()

# Run specific tool
ruff_result = checker.run_ruff()
mypy_result = checker.run_mypy()

# Or run everything
results = checker.run_all()

# Access structured errors
for tool, result in results.items():
    if not result.passed:
        for error in result.errors:
            # Each error has: file, line, column, code, message
            print(f"Fix {error['file']}:{error['line']} - {error['code']}")
```

**Data Structure**:
```python
CheckResult(
    tool="ruff",
    passed=False,
    errors=[
        {
            "file": "user.py",
            "line": 42,
            "column": 10,
            "code": "F401",           # Use this to determine fix!
            "message": "Unused import",
            "severity": "error"
        }
    ],
    suggestions=["Remove unused imports"],  # AI-actionable
    duration=1.5,
    exit_code=1
)
```

**Common Error Codes to Handle**:
- `F401`: Unused import → Remove it
- `F841`: Unused variable → Remove or use it
- `E501`: Line too long → Reformat
- `no-untyped-def`: Missing type hints → Add them
- `import-outside-toplevel`: Import not at top → Move it

## 🏗️ API 2: Code Generation (Replace CLI scaffold)

**When to use**: Creating new UseCases, Entities, Repositories

```python
generator = ScaffoldGenerator()

# Generate UseCase
result = generator.create_usecase(
    name="CreateOrder",
    input_type="CreateOrderInput",
    output_type="CreateOrderOutput",
    repository="OrderRepositoryPort"
)

# Modify code before writing (KEY FEATURE for AI!)
if result.success:
    code = result.code
    # AI can customize the code
    code = code.replace("# TODO: Implement", "# Custom implementation")

    # Write to suggested path
    with open(result.file_path, 'w') as f:
        f.write(code)

# Generate Entity
entity_result = generator.create_entity(
    name="Order",
    attributes=["customer_id", "total", "items"]
)
```

**Data Structure**:
```python
ScaffoldResult(
    component_type="usecase",
    name="CreateOrder",
    code="...",              # Full generated code as string
    file_path="src/...",     # Suggested location
    success=True,
    metadata={
        "imports": [...],    # Dependencies to check
        "input_type": "...",
        "output_type": "..."
    }
)
```

## 🔍 API 3: Component Discovery (Understand the codebase)

**When to use**: Before modifying architecture, understanding dependencies

```python
discovery = ComponentDiscovery()
result = discovery.scan_project()

# Access discovered components
for entity in result.entities:
    print(f"Entity: {entity.name} at {entity.file_path}:{entity.line_number}")

for usecase in result.usecases:
    print(f"UseCase: {usecase.name}")
    print(f"  Base: {usecase.base_class}")
    print(f"  Imports: {usecase.imports}")
```

**Data Structure**:
```python
ComponentInfo(
    name="Order",
    type="entity",
    file_path="src/domain/order.py",
    line_number=15,
    base_class="EntityBase",
    imports=["from forgebase.domain.entity_base import EntityBase"],
    docstring="Order domain entity"
)
```

## 🧪 API 4: Test Execution (Replace pytest commands)

**When to use**: Running tests, analyzing failures, checking coverage

```python
runner = TestRunner()

# Run specific test suite
unit_result = runner.run_unit_tests()
integration_result = runner.run_integration_tests()

# Or run all
results = runner.run_all()

# Analyze failures
for test_type, result in results.items():
    if not result.passed:
        for failure in result.failures:
            print(f"Failed: {failure.test_name}")
            print(f"  File: {failure.file}:{failure.line}")
            print(f"  Error: {failure.error_type}")
            print(f"  Message: {failure.message}")
```

**Data Structure**:
```python
TestResult(
    test_type="unit",
    passed=False,
    total=100,
    passed_count=95,
    failed_count=5,
    failures=[
        TestFailure(
            test_name="test_create_order",
            file="tests/test_order.py",
            line=42,
            error_type="AssertionError",
            message="Expected 200, got 404"
        )
    ],
    coverage=85.5
)
```

## 🎯 Complete Workflow Example

```python
from forgebase.dev.api import *

# 1. Discover what exists
discovery = ComponentDiscovery()
components = discovery.scan_project()
print(f"Found {len(components.entities)} entities")

# 2. Generate new component
generator = ScaffoldGenerator()
result = generator.create_usecase("ProcessPayment")
if result.success:
    # Customize before writing
    with open(result.file_path, 'w') as f:
        f.write(result.code)

# 3. Check quality
checker = QualityChecker()
quality_results = checker.run_all()

# 4. Fix errors automatically
for tool, result in quality_results.items():
    if not result.passed:
        for error in result.errors:
            if error.get("code") == "F401":  # Unused import
                # AI removes the import from error['file'] at error['line']
                pass

# 5. Run tests
runner = TestRunner()
test_results = runner.run_all()
if test_results["unit"].passed:
    print("✅ Ready to commit")
```

## 🧠 Decision-Making Guide for AI Agents

### When to use which API?

| Task | API | Method |
|------|-----|--------|
| "Check code quality" | QualityChecker | `run_all()` |
| "Fix linting errors" | QualityChecker | `run_ruff()` → analyze errors |
| "Add type hints" | QualityChecker | `run_mypy()` → find missing hints |
| "Create a UseCase" | ScaffoldGenerator | `create_usecase()` |
| "Create an Entity" | ScaffoldGenerator | `create_entity()` |
| "What entities exist?" | ComponentDiscovery | `scan_project()` → entities |
| "What are the dependencies?" | ComponentDiscovery | `scan_project()` → check imports |
| "Run tests" | TestRunner | `run_all()` or specific type |
| "Why are tests failing?" | TestRunner | `run_*()` → analyze failures |

### Error Code → Action Mapping

```python
ERROR_ACTIONS = {
    "F401": "Remove unused import",
    "F841": "Remove unused variable",
    "E501": "Break long line",
    "no-untyped-def": "Add type hints",
    "import-error": "Check dependencies",
    "AttributeError": "Check object attributes",
    "NameError": "Check variable exists",
}
```

## 📝 Best Practices for AI Agents

### ✅ DO:
1. **Import directly** - Use Python APIs, not subprocess CLI calls
2. **Check error codes** - Use `error['code']` to determine action
3. **Modify generated code** - Customize before writing files
4. **Use structured data** - Access `file`, `line`, `column` directly
5. **Run quality before commit** - Always check with `run_all()`

### ❌ DON'T:
1. **Don't parse CLI text output** - Use APIs instead
2. **Don't guess file locations** - Use discovery API
3. **Don't write code without checking** - Run quality checks first
4. **Don't ignore error codes** - They tell you exactly what to fix
5. **Don't subprocess** - Import and call directly

## 🔗 Integration Examples

### Claude Code Integration
```python
# In your Claude Code context:
from forgebase.dev.api import QualityChecker

checker = QualityChecker()
results = checker.run_all()

# Claude can now reason about specific errors
for error in results["ruff"].errors:
    if error["code"] == "F401":
        # Claude removes the import automatically
        pass
```

### Cursor Integration
```python
# In Cursor workspace:
from forgebase.dev.api import ScaffoldGenerator

generator = ScaffoldGenerator()
result = generator.create_usecase("UpdateProfile")

# Cursor modifies the generated code based on context
# then writes to result.file_path
```

### Aider Integration
```python
# In Aider session:
from forgebase.dev.api import TestRunner

runner = TestRunner()
results = runner.run_all()

# Aider analyzes failures and fixes them
for failure in results["unit"].failures:
    print(f"Aider, fix {failure.file}:{failure.line}")
```

## 📚 Full Documentation

- **Complete API Docs**: `src/forgebase/dev/AI_AGENTS.md`
- **Code Examples**: `examples/ai_agent_usage.py`
- **API Source**: `src/forgebase/dev/api/`

## 💡 Pro Tips

1. **Use `to_dict()` for logging**: All results have `.to_dict()` for JSON
2. **Check `success` first**: All operations have a `success` boolean
3. **Use metadata**: ScaffoldResult includes imports and dependencies
4. **Batch operations**: `run_all()` methods run everything at once
5. **Cross-platform**: All APIs work on Windows, macOS, Linux

---

**Version**: ForgeBase 0.1.3
**Updated**: 2025-11-04
**For**: AI Coding Agents
