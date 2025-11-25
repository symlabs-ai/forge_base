# ForgeBase AI Agent Ecosystem

**Complete guide to ForgeBase's AI-first developer experience.**

## 🎯 Vision

ForgeBase is designed for **AI coding agents as first-class users**. All developer tools expose **Python APIs with structured data**, enabling agents to reason about code quality, generate components, and fix issues autonomously.

## 🧠 ForgeBase Within The ForgeProcess Cycle

Before diving into the APIs, understand that ForgeBase is **part of a larger cognitive cycle**:

```
MDD (Market) → BDD (Behavior) → TDD (Test) → CLI (Execute) → Feedback
                                    ▲
                               ForgeBase
                             implements this
```

ForgeBase provides the **execution layer** where:
- **Behaviors** (from BDD) become **UseCases**
- **Tests** (from TDD) validate **implementations**
- **CLI** allows **observation** and **exploration**
- **Feedback** enables **continuous learning**

**For complete context**, see [docs/FORGE_PROCESS.md](docs/FORGE_PROCESS.md)

## 📊 Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     AI Coding Agents                         │
│  (Claude Code, Cursor, Copilot, Aider, Custom Agents)       │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  │ Import & Call
                  ▼
┌─────────────────────────────────────────────────────────────┐
│            ForgeBase Python APIs (v0.1.4)                    │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Quality      │  │ Scaffold     │  │ Discovery    │     │
│  │ Checker      │  │ Generator    │  │              │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐                       │
│  │ Test         │  │ Utils        │                       │
│  │ Runner       │  │              │                       │
│  └──────────────┘  └──────────────┘                       │
└─────────────────────────────────────────────────────────────┘
                  │
                  │ Structured Data (JSON/Dataclasses)
                  ▼
┌─────────────────────────────────────────────────────────────┐
│                   Underlying Tools                           │
│   (Ruff, Mypy, Pytest, import-linter, Deptry)              │
└─────────────────────────────────────────────────────────────┘
```

## 📚 Documentation Levels

ForgeBase provides **4 levels** of documentation for different needs:

### 1. Quick Start (300 lines)
**File**: `AI_AGENT_QUICK_START.md`
**Audience**: AI agents needing fast reference
**Contents**:
- API imports and signatures
- Data structure formats
- Error code → action mappings
- Decision guide (when to use what)
- Complete workflow example

**Use when**: Adding to context window, quick lookup

### 2. Complete Guide (500 lines)
**File**: `src/forgebase/dev/AI_AGENTS.md`
**Audience**: AI agents needing detailed docs
**Contents**:
- Comprehensive API documentation
- All parameters and return types
- Integration patterns
- Best practices
- Troubleshooting

**Use when**: Deep integration, understanding all features

### 3. Claude-Specific Instructions (800 lines)
**File**: `.claude/forgebase_instructions.md`
**Audience**: Claude Code specifically
**Contents**:
- Task → API mappings
- Reasoning guidelines for Claude
- Complete data structure reference
- DO/DON'T anti-patterns
- Performance tips
- Verification checklist

**Use when**: Configuring Claude Code for this project

### 4. Executable Examples (350-400 lines each)
**Files**:
- `examples/ai_agent_usage.py`
- `examples/claude_api_integration.py`

**Audience**: Developers and AI agents
**Contents**:
- Working code examples
- All 4 APIs demonstrated
- Complete workflows
- Integration patterns

**Use when**: Learning by doing, copy-paste templates

## 🔄 Information Flow

```
User Request
    ↓
AI Agent reads instructions (.claude/, AI_AGENT_QUICK_START.md)
    ↓
Agent imports APIs (from forgebase.dev.api import *)
    ↓
Agent calls API with parameters
    ↓
API returns structured data (dataclasses with to_dict())
    ↓
Agent reasons about data (error codes, file:line, etc.)
    ↓
Agent takes action (fix, generate, analyze)
    ↓
Agent verifies (run quality checks)
    ↓
Agent reports to user (with file:line references)
```

## 🎭 Agent Personas & Usage

### Claude Code (This AI)

**Configuration**: `.claude/forgebase_instructions.md` loaded automatically

**Typical workflow**:
```python
# User: "Fix the linting errors"

from forgebase.dev.api import QualityChecker

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

### Claude API (Programmatic)

**Configuration**: System prompt + ForgeBase API calls

**Typical workflow**:
```python
# Developer creates agent
agent = ClaudeForgeBaseAgent()

# Agent analyzes autonomously
analysis = agent.analyze_codebase()
fixes = agent.fix_quality_issues()
tests = agent.run_tests_and_fix()

# Agent reports structured results
```

**Strengths**:
- Autonomous operation
- Batch processing
- API-driven workflows
- Integration with CI/CD

### Cursor

**Configuration**: `.cursorrules` + context

**Typical workflow**:
```
User highlights code → asks "improve this"
→ Cursor uses ComponentDiscovery to understand context
→ Cursor uses ScaffoldGenerator if creating new components
→ Cursor uses QualityChecker to verify changes
→ Cursor shows diff with improvements
```

**Strengths**:
- IDE integration
- Real-time feedback
- Multi-file awareness

### GitHub Copilot

**Configuration**: Comments + API imports

**Typical workflow**:
```python
# AI: Use ForgeBase QualityChecker API
from forgebase.dev.api import QualityChecker

# Copilot suggests rest of the code...
```

**Strengths**:
- Inline suggestions
- Fast iteration
- Context-aware completions

### Aider

**Configuration**: `.aider.conf.yml` + instructions

**Typical workflow**:
```bash
aider --message "Create a UseCase for processing orders"
# Aider uses ScaffoldGenerator
# Aider customizes generated code
# Aider runs QualityChecker
# Aider commits if passing
```

**Strengths**:
- Git-aware
- Multi-file edits
- Autonomous commits

## 🛠️ Available APIs

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
        "code": "F401",  # ← Agent uses this to decide action
        "message": "Unused import",
        "severity": "error"
    }],
    suggestions=["Remove unused imports"],
    duration=1.5
)
```

**Agent Decision Making**:
- `F401` → Remove unused import
- `F841` → Remove unused variable
- `no-untyped-def` → Add type hints
- `E501` → Break long line

### 2. ScaffoldGenerator
**Purpose**: Boilerplate code generation with customization

**Returns**:
```python
ScaffoldResult(
    component_type="usecase",
    name="CreateOrder",
    code="...",  # ← Full code as string for modification
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
- Understanding existing architecture
- Finding related components
- Checking naming conventions
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

## 🎯 Key Benefits for AI Agents

### ✅ No Text Parsing Required
```python
# ❌ Old way (CLI)
output = subprocess.run(["devtool", "quality"]).stdout
errors = parse_text(output)  # Fragile!

# ✅ New way (API)
result = QualityChecker().run_all()
errors = result["ruff"].errors  # Structured!
```

### ✅ Direct Error Location Access
```python
# Agent can immediately locate and fix
for error in result.errors:
    file = error['file']      # "src/domain/user.py"
    line = error['line']      # 42
    code = error['code']      # "F401"
    # Agent knows exactly where and what to fix
```

### ✅ Code Reasoning via Error Codes
```python
# Agent can reason about specific error types
if error['code'] == 'F401':
    # Agent knows: Unused import → remove it
    action = "remove_import"
elif error['code'] == 'no-untyped-def':
    # Agent knows: Missing types → add them
    action = "add_type_hints"
```

### ✅ Code Modification Before Writing
```python
# Agent can customize generated code
result = generator.create_usecase("ProcessPayment")
code = result.code

# Agent modifies for requirements
code = add_business_logic(code)
code = add_validation(code)

# Then write
write_file(result.file_path, code)
```

### ✅ Architectural Understanding
```python
# Agent can analyze codebase structure
discovery = ComponentDiscovery()
components = discovery.scan_project()

# Agent can reason about architecture
print(f"This is a {len(components.entities)}-entity system")
print(f"With {len(components.usecases)} use cases")
print(f"Using {len(components.repositories)} repositories")
```

## 📈 Adoption Path

### Phase 1: Basic Usage (Current)
- ✅ APIs available and documented
- ✅ Examples provided
- ✅ Instructions for agents

**Agents can**: Run quality checks, generate code, discover components

### Phase 2: Enhanced Integration (Future)
- 🔄 Cursor/Copilot plugins
- 🔄 Aider custom commands
- 🔄 VSCode extension

**Agents can**: Use APIs directly from IDE

### Phase 3: Autonomous Development (Future)
- 🔄 Full workflow automation
- 🔄 Self-healing codebases
- 🔄 Continuous quality enforcement

**Agents can**: Develop features end-to-end with minimal human input

## 🔄 ForgeProcess: The Full Cognitive Cycle

### Understanding the Bigger Picture

ForgeBase APIs are **part of a cognitive development cycle** called **ForgeProcess**. AI agents should understand this cycle to reason about **why** they're doing certain actions.

```
┌────────────────────────────────────────────────────┐
│ 1. MDD (Market Driven Development)                 │
│    PORQUÊ existir? → forge.yaml                    │
│    Defines: ValueTracks, Value KPIs                │
└────────────────┬───────────────────────────────────┘
                 │ Translation: Value → Behavior
                 ▼
┌────────────────────────────────────────────────────┐
│ 2. BDD (Behavior Driven Development)               │
│    O QUÊ fazer? → .feature files                   │
│    Defines: Scenarios (Given/When/Then)            │
└────────────────┬───────────────────────────────────┘
                 │ Implementation: Behavior → Code
                 ▼
┌────────────────────────────────────────────────────┐
│ 3. TDD (Test Driven Development)                   │
│    COMO implementar? → tests/                      │
│    Proves: Code works as specified                 │
└────────────────┬───────────────────────────────────┘
                 │ Manifestation: Code → Execution
                 ▼
┌────────────────────────────────────────────────────┐
│ 4. CLI (Interface Cognitiva)                       │
│    Executar e observar → forgebase CLI             │
│    ← AI AGENTS USE APIs HERE ←                     │
│    Collects: Logs, Metrics, Traces                 │
└────────────────┬───────────────────────────────────┘
                 │ Collection: Evidence → Learning
                 ▼
┌────────────────────────────────────────────────────┐
│ 5. Feedback (Reflexão)                             │
│    Aprender e ajustar → feedback reports           │
│    Informs: MDD improvements, BDD refinements      │
└────────────────┬───────────────────────────────────┘
                 │
                 └─────> Loop back to MDD
```

### How AI Agents Fit In

**AI agents using ForgeBase APIs operate at Phase 3-4:**

1. **Phase 3 (TDD)**:
   - Use `ScaffoldGenerator` to create test-driven code
   - Use `QualityChecker` to validate implementation
   - Ensure code passes tests

2. **Phase 4 (CLI)**:
   - Use `TestRunner` to execute and observe
   - Use `ComponentDiscovery` to understand architecture
   - Collect metrics and traces

3. **Phase 5 (Feedback)**:
   - Analyze quality results
   - Compare against Value KPIs (from Phase 1)
   - Suggest improvements

### Agent Reasoning Example

```python
# AI Agent understands the FULL cycle

# 1. Read MDD (context: WHY this system exists)
with open("forge.yaml") as f:
    mdd = yaml.load(f)
    value_track = mdd["value_tracks"]["IssueInvoice"]
    kpi = "0% errors in tax calculation"

# 2. Read BDD (context: WHAT behaviors are expected)
with open("features/issue_invoice.feature") as f:
    bdd = f.read()
    # AI understands: "Given order, When issue, Then ICMS correct"

# 3. TDD (AI implements with proof)
from forgebase.dev.api import ScaffoldGenerator, QualityChecker

generator = ScaffoldGenerator()
result = generator.create_usecase("IssueInvoice")

# AI customizes based on BDD
code = customize_for_behavior(result.code, bdd)
write_file(result.file_path, code)

# AI validates
checker = QualityChecker()
quality = checker.run_all()
assert all(r.passed for r in quality.values())

# 4. CLI (AI observes execution)
from forgebase.dev.api import TestRunner

runner = TestRunner()
tests = runner.run_all()

# 5. Feedback (AI reasons about results)
if tests["unit"].passed:
    # Check if KPI is met
    kpi_met = check_kpi(kpi, tests)
    if kpi_met:
        print("✅ ValueTrack 'IssueInvoice' is delivering value!")
    else:
        print("⚠️ KPI not met, suggest improvements...")
```

### Key Insight for AI Agents

**Don't just fix code blindly**. Understand:
- **WHY** it exists (MDD / forge.yaml)
- **WHAT** it should do (BDD / .feature)
- **HOW** to prove it works (TDD / tests)
- **OBSERVE** actual behavior (CLI / APIs)
- **LEARN** from results (Feedback)

This makes AI agents **context-aware** and **value-driven**, not just code generators.

### ForgeProcess Documentation

| Document | Purpose | For AI Agents |
|----------|---------|---------------|
| [FORGE_PROCESS.md](docs/FORGE_PROCESS.md) | Complete cycle explanation | Understand WHY |
| [FORGE_PROCESS_VISUAL_GUIDE.md](docs/FORGE_PROCESS_VISUAL_GUIDE.md) | Diagrams and examples | Visual learning |
| [ADR-006](docs/adr/006-forgeprocess-integration.md) | Technical integration | Deep dive |

## 🔗 Quick Links

| Resource | Location | Use For |
|----------|----------|---------|
| **ForgeProcess Docs** | `/docs/FORGE_PROCESS.md` | Understanding the cycle |
| **Visual Guide** | `/docs/FORGE_PROCESS_VISUAL_GUIDE.md` | Diagrams and examples |
| Quick Reference | `/AI_AGENT_QUICK_START.md` | Fast API lookup |
| Complete Docs | `/src/forgebase/dev/AI_AGENTS.md` | Detailed reference |
| Claude Instructions | `/.claude/forgebase_instructions.md` | Claude Code config |
| Python Examples | `/examples/ai_agent_usage.py` | Learning by example |
| Claude API Integration | `/examples/claude_api_integration.py` | Programmatic use |
| API Source Code | `/src/forgebase/dev/api/*.py` | Deep understanding |

## 🎓 Learning Resources

### For AI Agents (Recommended Order):
1. **Start**: Read `AI_AGENT_QUICK_START.md` (5 min)
2. **Learn**: Study `examples/ai_agent_usage.py` (10 min)
3. **Practice**: Try each API with sample code (20 min)
4. **Master**: Read complete docs `src/forgebase/dev/AI_AGENTS.md` (30 min)

### For Developers Building AI Agents:
1. **Start**: Read this document (10 min)
2. **Explore**: Check `examples/claude_api_integration.py` (15 min)
3. **Build**: Create your own agent using ForgeBase APIs (1 hour)
4. **Optimize**: Study `.claude/forgebase_instructions.md` for patterns (30 min)

## 💡 Success Metrics

An AI agent is **successfully using ForgeBase APIs** when:

- ✅ Imports from `forgebase.dev.api` (not using CLI)
- ✅ Accesses error dictionaries directly (not parsing text)
- ✅ Uses error codes for decision making (not guessing)
- ✅ Modifies generated code before writing (not using as-is)
- ✅ Runs quality checks before completing tasks (not assuming)
- ✅ Reports file:line references to users (not vague messages)

## 🚀 Next Steps

### For You (Project Owner):
1. ✅ APIs are ready (`src/forgebase/dev/api/`)
2. ✅ Documentation is complete (4 levels)
3. ✅ Examples are provided (2 files)
4. ✅ Claude is configured (`.claude/` directory)

### For AI Agents:
1. 📖 Read your specific instructions (see Quick Links)
2. 🔧 Import and try the APIs
3. 🧪 Run examples to learn patterns
4. 🚀 Start using for real tasks

### For Developers:
1. 📚 Study the integration examples
2. 🛠️ Build custom agents using ForgeBase APIs
3. 🔄 Integrate with your CI/CD pipeline
4. 📊 Monitor agent performance and quality

---

**Version**: ForgeBase 0.1.4
**Created**: 2025-11-04
**Status**: Production Ready
**Audience**: AI Agents, Developers, Project Owners
