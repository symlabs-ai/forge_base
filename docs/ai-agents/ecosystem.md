# ForgeBase AI Agent Ecosystem

**Complete guide to ForgeBase's AI-first developer experience.**

## Vision

ForgeBase is designed with **AI code agents as first-class users**. All developer tools expose **Python APIs with structured data**, enabling agents to reason about code quality, generate components, and fix issues autonomously.

## ForgeBase Within the ForgeProcess Cycle

Before diving into the APIs, understand that ForgeBase is **part of a larger cognitive cycle**:

```
MDD (Market) -> BDD (Behavior) -> TDD (Test) -> CLI (Execute) -> Feedback
                                       ^
                                  ForgeBase
                                implements this
```

ForgeBase provides the **execution layer** where:
- **Behaviors** (from BDD) become **UseCases**
- **Tests** (from TDD) validate **implementations**
- **CLI** enables **observation** and **exploration**
- **Feedback** enables **continuous learning**

## Architecture Overview

```
+-------------------------------------------------------------+
|                     AI Code Agents                            |
|  (Claude Code, Cursor, Copilot, Aider, Custom Agents)        |
+-----------------+-------------------------------------------+
                  |
                  | Import & Call
                  v
+-------------------------------------------------------------+
|            ForgeBase Python APIs (v0.1.4)                     |
|                                                               |
|  +--------------+  +--------------+  +--------------+         |
|  | Quality      |  | Scaffold     |  | Discovery    |         |
|  | Checker      |  | Generator    |  |              |         |
|  +--------------+  +--------------+  +--------------+         |
|                                                               |
|  +--------------+  +--------------+                           |
|  | Test         |  | Utils        |                           |
|  | Runner       |  |              |                           |
|  +--------------+  +--------------+                           |
+-------------------------------------------------------------+
                  |
                  | Structured Data (JSON/Dataclasses)
                  v
+-------------------------------------------------------------+
|                   Underlying Tools                            |
|   (Ruff, Mypy, Pytest, import-linter, Deptry)                |
+-------------------------------------------------------------+
```

---

## Documentation Levels

ForgeBase provides **4 levels** of documentation for different needs:

### 1. Quick Start
**File**: `docs/ai-agents/quick-start.md`
**Audience**: AI agents needing a quick reference
**Content**:
- Imports and API signatures
- Data structure formats
- Error code -> action mappings
- Decision guide (when to use what)
- Complete workflow example

**Use when**: Adding to context window, quick lookup

### 2. Complete Guide
**File**: `docs/ai-agents/complete-guide.md`
**Audience**: AI agents needing detailed docs
**Content**:
- Full API documentation
- All parameters and return types
- Integration patterns
- Best practices
- Troubleshooting

**Use when**: Deep integration, understanding all features

### 3. Runnable Examples
**Files**:
- `examples/ai_agent_usage.py`
- `examples/claude_api_integration.py`

**Audience**: Developers and AI agents
**Content**:
- Working code examples
- All 4 APIs demonstrated
- Complete workflows
- Integration patterns

**Use when**: Learning by doing, copy-paste templates

---

## Information Flow

```
User Request
    |
AI Agent reads instructions (docs/ai-agents/)
    |
Agent imports APIs (from forge_base.dev.api import *)
    |
Agent calls API with parameters
    |
API returns structured data (dataclasses with to_dict())
    |
Agent reasons about data (error codes, file:line, etc.)
    |
Agent takes action (fix, generate, analyze)
    |
Agent verifies (run quality checks)
    |
Agent reports to user (with file:line references)
```

---

## Agent Personas & Usage

### Claude Code

**Typical workflow**:
```python
# User: "Fix the linting errors"

from forge_base.dev.api import QualityChecker

checker = QualityChecker()
results = checker.run_all()

for tool, result in results.items():
    if not result.passed:
        for error in result.errors:
            if error['code'] == 'F401':  # I know what to do
                remove_unused_import(error['file'], error['line'])
```

**Strengths**:
- Context-aware (sees project files)
- Can read and edit files directly
- Verifies changes immediately

### Cursor

**Typical workflow**:
```
User highlights code -> asks "improve this"
-> Cursor uses ComponentDiscovery to understand context
-> Cursor uses ScaffoldGenerator if creating new components
-> Cursor uses QualityChecker to verify changes
-> Cursor shows diff with improvements
```

**Strengths**:
- IDE integration
- Real-time feedback
- Multi-file awareness

### GitHub Copilot

**Typical workflow**:
```python
# AI: Use ForgeBase QualityChecker API
from forge_base.dev.api import QualityChecker

# Copilot suggests the rest of the code...
```

**Strengths**:
- Inline suggestions
- Fast iteration
- Context-aware completions

### Aider

**Typical workflow**:
```bash
aider --message "Create a UseCase for processing orders"
# Aider uses ScaffoldGenerator
# Aider customizes the generated code
# Aider runs QualityChecker
# Aider commits if it passes
```

**Strengths**:
- Git-aware
- Multi-file edits
- Autonomous commits

---

## Available APIs

### 1. QualityChecker
**Purpose**: Code quality validation with structured results

**Returns**:
```python
CheckResult(
    tool="ruff",
    passed=False,
    errors=[{
        "file": "user.py",
        "line": 42,
        "column": 10,
        "code": "F401",  # <- Agent uses this to decide action
        "message": "Unused import",
        "severity": "error"
    }],
    suggestions=["Remove unused imports"],
    duration=1.5
)
```

**Agent Decision-Making**:
- `F401` -> Remove unused import
- `F841` -> Remove unused variable
- `no-untyped-def` -> Add type hints
- `E501` -> Break long line

### 2. ScaffoldGenerator
**Purpose**: Boilerplate code generation with customization

**Returns**:
```python
ScaffoldResult(
    component_type="usecase",
    name="CreateOrder",
    code="...",  # <- Full code as a string for modification
    file_path="src/application/create_order_usecase.py",
    metadata={
        "imports": [...],
        "dependencies": ["OrderRepositoryPort"],
        "input_type": "CreateOrderInput",
        "output_type": "CreateOrderOutput"
    }
)
```

**Agent Workflow**:
1. Generate boilerplate
2. Modify code for requirements
3. Write to file_path
4. Verify with QualityChecker

### 3. ComponentDiscovery
**Purpose**: Codebase analysis and cataloging

**Returns**:
```python
DiscoveryResult(
    entities=[
        ComponentInfo(
            name="Order",
            type="entity",
            file_path="src/domain/order.py",
            line_number=15,
            base_class="EntityBase"
        )
    ],
    usecases=[...],
    repositories=[...],
    total_files_scanned=42
)
```

**Agent Use Cases**:
- Understand existing architecture
- Find related components
- Verify naming conventions
- Dependency analysis

### 4. TestRunner
**Purpose**: Test execution with structured failures

**Returns**:
```python
TestResult(
    test_type="unit",
    passed=False,
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

**Agent Analysis**:
- Which tests failed
- Exact failure location
- Error type for root cause
- Coverage for completeness

---

## Key Benefits for AI Agents

### No Text Parsing Needed
```python
# Old method (CLI)
output = subprocess.run(["devtool", "quality"]).stdout
errors = parse_text(output)  # Fragile!

# New method (API)
result = QualityChecker().run_all()
errors = result["ruff"].errors  # Structured!
```

### Direct Access to Error Location
```python
# Agent can locate and fix immediately
for error in result.errors:
    file = error['file']      # "src/domain/user.py"
    line = error['line']      # 42
    code = error['code']      # "F401"
    # Agent knows exactly where and what to fix
```

### Code Reasoning via Error Codes
```python
# Agent can reason about specific error types
if error['code'] == 'F401':
    # Agent knows: Unused import -> remove
    action = "remove_import"
elif error['code'] == 'no-untyped-def':
    # Agent knows: Missing types -> add
    action = "add_type_hints"
```

### Code Modification Before Writing
```python
# Agent can customize generated code
result = generator.create_usecase("ProcessPayment")
code = result.code

# Agent modifies for requirements
code = add_business_logic(code)
code = add_validation(code)

# Then writes
write_file(result.file_path, code)
```

### Architectural Understanding
```python
# Agent can analyze codebase structure
discovery = ComponentDiscovery()
components = discovery.scan_project()

# Agent can reason about architecture
print(f"This is a {len(components.entities)}-entity system")
print(f"With {len(components.usecases)} use cases")
print(f"Using {len(components.repositories)} repositories")
```

---

## Adoption Path

### Phase 1: Basic Usage (Current)
- APIs available and documented
- Examples provided
- Agent instructions included

**Agents can**: Run quality checks, generate code, discover components

### Phase 2: Enhanced Integration (Future)
- Cursor/Copilot plugins
- Custom Aider commands
- VSCode extension

**Agents can**: Use APIs directly from the IDE

### Phase 3: Autonomous Development (Future)
- Full workflow automation
- Self-healing codebases
- Continuous quality enforcement

**Agents can**: Develop features end-to-end with minimal human input

---

## Success Metrics

An AI agent is **successfully using ForgeBase APIs** when:

- It imports from `forge_base.dev.api` (not using CLI)
- It accesses error dictionaries directly (not parsing text)
- It uses error codes for decision-making (not guessing)
- It modifies generated code before writing (not using as-is)
- It runs quality checks before completing tasks (not assuming)
- It reports file:line references to users (not vague messages)

---

## Quick Links

| Resource | Location | Use For |
|----------|----------|---------|
| Quick Start | `docs/ai-agents/quick-start.md` | Quick API lookup |
| Complete Guide | `docs/ai-agents/complete-guide.md` | Detailed reference |
| Discovery | `docs/ai-agents/discovery.md` | How to discover APIs |
| Python Examples | `examples/ai_agent_usage.py` | Learn by example |
| API Source Code | `src/forge_base/dev/api/*.py` | Deep understanding |

---

**Version**: ForgeBase 0.1.4
**Status**: Production Ready
**Audience**: AI Agents, Developers, Project Owners
