# ForgeBase Development Instructions for Claude

## 🚨 FIRST TIME HERE? START HERE! 🚨

**If you've never worked with this ForgeBase project before:**

```python
# 1. Get the complete API documentation programmatically
from forgebase.dev import get_agent_quickstart

guide = get_agent_quickstart()
print(guide)  # Full API reference with examples

# This documentation is embedded in the package and works offline!
# It contains all APIs, error codes, data structures, and workflows.
```

**Why this matters:**
- ✅ Comprehensive API guide (9000+ chars)
- ✅ Error code mappings (F401 → Remove import, etc.)
- ✅ Data structure specs (CheckResult, ScaffoldResult, etc.)
- ✅ Complete workflow examples
- ✅ Always in sync with installed version

**After reading the guide above, continue with the quick reference below.**

---

## 🤖 Core Directive

**ALWAYS use ForgeBase Python APIs instead of CLI commands or subprocess calls.**

## 📚 Quick Import Reference

```python
from forgebase.dev.api import (
    QualityChecker,      # Code quality validation
    ScaffoldGenerator,   # Code generation
    ComponentDiscovery,  # Codebase analysis
    TestRunner,          # Test execution
)
```

## 🎯 Task → API Mapping

### Quality & Linting Tasks
```python
# User: "Check code quality" or "Fix linting errors"
checker = QualityChecker()
results = checker.run_all()

# Access structured errors - NO TEXT PARSING
for tool, result in results.items():
    if not result.passed:
        for error in result.errors:
            # error = {file, line, column, code, message}
            print(f"Fix {error['code']} at {error['file']}:{error['line']}")
```

### Code Generation Tasks
```python
# User: "Create a UseCase" or "Generate an Entity"
generator = ScaffoldGenerator()

# Generate UseCase
result = generator.create_usecase(
    name="ProcessPayment",
    input_type="PaymentInput",
    output_type="PaymentOutput",
    repository="PaymentRepositoryPort"
)

# IMPORTANT: Modify code before writing
if result.success:
    code = result.code
    # Customize based on user requirements
    code = customize_for_context(code)
    # Write to suggested path
    write_file(result.file_path, code)
```

### Discovery Tasks
```python
# User: "What entities exist?" or "Show me the architecture"
discovery = ComponentDiscovery()
components = discovery.scan_project()

# Access structured component info
print(f"Entities: {len(components.entities)}")
print(f"UseCases: {len(components.usecases)}")
print(f"Repositories: {len(components.repositories)}")
```

### Testing Tasks
```python
# User: "Run tests" or "Why are tests failing?"
runner = TestRunner()
results = runner.run_all()

# Access structured test failures
for test_type, result in results.items():
    if not result.passed:
        for failure in result.failures:
            # failure = TestFailure(test_name, file, line, error_type, message)
            print(f"Failed: {failure.test_name}")
            print(f"  {failure.file}:{failure.line}")
            print(f"  {failure.error_type}: {failure.message}")
```

## 🔧 Error Code → Fix Action

**Memorize these common mappings:**

| Error Code | Tool | Action |
|------------|------|--------|
| F401 | Ruff | Remove unused import at specified line |
| F841 | Ruff | Remove unused variable |
| E501 | Ruff | Break long line (respecting line-length=100) |
| I001 | Ruff | Fix import sorting (use ruff --fix) |
| no-untyped-def | Mypy | Add type hints to function |
| import-error | Mypy | Check module exists or add dependency |
| arg-type | Mypy | Fix argument type mismatch |
| return-value | Mypy | Fix return type |

## 🎬 Complete Workflow Example

```python
# Typical ForgeBase development workflow

# 1. User asks: "Create a new UseCase for updating user profiles"
from forgebase.dev.api import ScaffoldGenerator, QualityChecker, TestRunner

# Generate boilerplate
generator = ScaffoldGenerator()
result = generator.create_usecase(
    name="UpdateUserProfile",
    input_type="UpdateProfileInput",
    output_type="UpdateProfileOutput",
    repository="UserRepositoryPort"
)

# Customize generated code
code = result.code
# Add business logic based on user requirements
code = add_validation_logic(code)
code = add_repository_calls(code)

# Write file
write_file(result.file_path, code)

# 2. Check quality
checker = QualityChecker()
quality_results = checker.run_all()

# 3. Fix any errors automatically
if not quality_results["ruff"].passed:
    for error in quality_results["ruff"].errors:
        if error["code"] == "F401":
            remove_unused_import(error["file"], error["line"])
        elif error["code"] == "I001":
            # Ruff can auto-fix this
            run_ruff_fix(error["file"])

# 4. Run tests
runner = TestRunner()
test_results = runner.run_all()

# 5. Report to user
if all(r.passed for r in test_results.values()):
    print("✅ UseCase created successfully!")
    print(f"   Location: {result.file_path}")
    print(f"   All quality checks passed")
    print(f"   All tests passing")
else:
    print("⚠️ UseCase created but tests are failing:")
    for failure in test_results["unit"].failures:
        print(f"   - {failure.test_name}: {failure.message}")
```

## 🚫 DON'Ts - Anti-Patterns to Avoid

### ❌ DON'T Use CLI
```python
# BAD - Don't do this:
result = subprocess.run(["devtool", "quality"], capture_output=True)
output = result.stdout.decode()  # Text parsing required
errors = parse_text_output(output)  # Error-prone
```

### ✅ DO Use Python API
```python
# GOOD - Do this instead:
from forgebase.dev.api import QualityChecker
checker = QualityChecker()
results = checker.run_all()  # Structured data
errors = results["ruff"].errors  # Direct access
```

### ❌ DON'T Parse Text
```python
# BAD - Don't parse CLI output:
for line in output.split("\n"):
    if "error" in line:
        # Fragile text parsing
        match = re.search(r"(\w+\.py):(\d+)", line)
```

### ✅ DO Use Structured Data
```python
# GOOD - Use structured error objects:
for error in results["ruff"].errors:
    file = error["file"]      # Direct access
    line = error["line"]      # Type-safe
    code = error["code"]      # Reliable
```

## 🧠 Reasoning Guidelines for Claude

### When User Says: "Fix the code quality issues"

**Your thought process:**
1. ✅ Use `QualityChecker().run_all()` to get structured errors
2. ✅ Analyze `error['code']` to determine the fix
3. ✅ Apply fixes based on error code mapping
4. ✅ Re-run quality check to verify
5. ❌ DON'T run CLI commands and parse output

**Implementation:**
```python
checker = QualityChecker()
results = checker.run_all()

for tool, result in results.items():
    for error in result.errors:
        # Use error code to determine action
        if error["code"] == "F401":
            # I know exactly what to do: remove unused import
            remove_import(error["file"], error["line"])
        elif error["code"] == "no-untyped-def":
            # I know exactly what to do: add type hints
            add_type_hints(error["file"], error["line"])
```

### When User Says: "Create a new UseCase"

**Your thought process:**
1. ✅ Ask for UseCase name and details if not provided
2. ✅ Use `ScaffoldGenerator().create_usecase()`
3. ✅ Get code as string, modify based on requirements
4. ✅ Write to file
5. ✅ Run quality checks
6. ❌ DON'T write code from scratch, use generator

**Implementation:**
```python
generator = ScaffoldGenerator()
result = generator.create_usecase(
    name="CreateOrder",
    input_type="CreateOrderInput",
    output_type="CreateOrderOutput",
    repository="OrderRepositoryPort"
)

# Customize the generated code
code = result.code
# Add business logic, validation, etc.
code = add_business_logic(code, user_requirements)

# Write and verify
write_file(result.file_path, code)
verify_quality(result.file_path)
```

### When User Says: "What's in the codebase?"

**Your thought process:**
1. ✅ Use `ComponentDiscovery().scan_project()`
2. ✅ Access structured component information
3. ✅ Provide organized summary
4. ❌ DON'T use grep/find to search manually

**Implementation:**
```python
discovery = ComponentDiscovery()
components = discovery.scan_project()

# Structured access to everything
print(f"📦 Codebase Analysis:")
print(f"   Entities: {len(components.entities)}")
print(f"   UseCases: {len(components.usecases)}")
print(f"   Repositories: {len(components.repositories)}")

for entity in components.entities:
    print(f"   - {entity.name} ({entity.file_path}:{entity.line_number})")
```

## 📊 Data Structures Reference

### CheckResult (from QualityChecker)
```python
{
    "tool": "ruff",
    "passed": False,
    "errors": [
        {
            "file": "src/domain/user.py",
            "line": 42,
            "column": 10,
            "code": "F401",
            "message": "Unused import: sys",
            "severity": "error"
        }
    ],
    "warnings": [...],
    "suggestions": ["Remove unused imports"],
    "duration": 1.5,
    "exit_code": 1
}
```

### ScaffoldResult (from ScaffoldGenerator)
```python
{
    "component_type": "usecase",
    "name": "CreateOrder",
    "code": "\"\"\"CreateOrder UseCase...\"\"\"",  # Full code as string
    "file_path": "src/application/create_order_usecase.py",
    "success": True,
    "metadata": {
        "imports": ["from forgebase.application.usecase_base import UseCaseBase"],
        "dependencies": ["OrderRepositoryPort"],
        "input_type": "CreateOrderInput",
        "output_type": "CreateOrderOutput"
    }
}
```

### ComponentInfo (from ComponentDiscovery)
```python
{
    "name": "Order",
    "type": "entity",
    "file_path": "src/domain/order.py",
    "line_number": 15,
    "base_class": "EntityBase",
    "imports": ["from forgebase.domain.entity_base import EntityBase"],
    "docstring": "Order domain entity"
}
```

### TestResult (from TestRunner)
```python
{
    "test_type": "unit",
    "passed": False,
    "total": 100,
    "passed_count": 95,
    "failed_count": 5,
    "failures": [
        {
            "test_name": "test_create_order",
            "file": "tests/unit/test_order.py",
            "line": 42,
            "error_type": "AssertionError",
            "message": "Expected 200, got 404",
            "traceback": "..."
        }
    ],
    "coverage": 85.5,
    "duration": 5.2
}
```

## 💡 Pro Tips for Claude

1. **Always check `success` first**: Every API result has a `success` boolean
2. **Use error codes for decisions**: Don't guess, use the `code` field
3. **Modify generated code**: ScaffoldGenerator returns strings for customization
4. **Use to_dict() for logging**: All results are JSON-serializable
5. **Check metadata**: ScaffoldResult includes useful dependency info
6. **Batch with run_all()**: More efficient than running tools individually
7. **Handle cross-platform**: APIs work everywhere, no platform checks needed

## 🎓 Learning Resources

- **Quick Start**: `AI_AGENT_QUICK_START.md` (300 lines, fast reference)
- **Complete Docs**: `src/forgebase/dev/AI_AGENTS.md` (500 lines, detailed)
- **Code Examples**: `examples/ai_agent_usage.py` (350 lines, runnable)
- **API Source**: `src/forgebase/dev/api/*.py` (read for deep understanding)

## 🚀 Performance Tips

1. **Import once**: Import APIs at session start, reuse instances
2. **Use run_all()**: Single call instead of multiple subprocess calls
3. **Cache discovery**: ComponentDiscovery is expensive, cache results
4. **Parallel checks**: Quality tools run independently, results arrive together
5. **No subprocess overhead**: Direct Python calls are faster than CLI

## ✅ Checklist for Claude

Before completing any task, verify:

- [ ] Used Python APIs (not CLI)
- [ ] Checked error codes (not text parsing)
- [ ] Modified generated code (not written from scratch)
- [ ] Ran quality checks (QualityChecker)
- [ ] Ran tests (TestRunner)
- [ ] Used structured data (accessed dictionaries directly)
- [ ] Provided clear feedback to user (with file:line references)

---

**Version**: ForgeBase 0.1.3
**Last Updated**: 2025-11-04
**For**: Claude Code & Claude API
