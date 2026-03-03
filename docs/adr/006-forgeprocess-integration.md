# ADR-006: ForgeProcess Integration

## Status

**Accepted** (2025-11-03)
**Updated** (2025-11-04) - Added full cognitive cycle context

## Context

ForgeBase is the **execution core** of the Forge Framework, but it does not exist in isolation. It is the **technical manifestation** of the intents captured by ForgeProcess.

### The Complete Cognitive Cycle

ForgeProcess is not just YAML ↔ Code synchronization. It is a **cognitive cycle** with 5 phases:

```
MDD (Value) → BDD (Behavior) → TDD (Proof) → CLI (Execution) → Feedback (Learning)
```

**Phase 1 - MDD (Market Driven Development)**: Defines **WHY** the system exists
- Specifies market value in `forge.yaml`
- Defines ValueTracks and SupportTracks
- Establishes Value KPIs

**Phase 2 - BDD (Behavior Driven Development)**: Defines **WHAT** the system does
- Translates value into verifiable behavior (`.feature` files)
- Specifies scenarios in Gherkin (Given/When/Then)
- Documents business rules

**MDD → BDD Transition**: The critical moment where **value intent** transforms into **observable behavior**.

**Phase 3 - TDD (Test Driven Development)**: Proves **HOW** to implement
- Each behavior becomes a test (Red-Green-Refactor)
- Tests are living technical memory
- Code is born validated

**Phase 4 - CLI (Cognitive Interface)**: **Execute and observe**
- Symbolic test environment
- Humans and AI can explore behaviors
- Collects logs, metrics, traces

**Phase 5 - Feedback (Reflection)**: **Learn and adjust**
- Operational Feedback: metrics, errors, performance
- Value Feedback: KPIs, stakeholders, users
- Learning loop closes the cycle

### ForgeBase ↔ ForgeProcess Integration

Within this cognitive cycle, ForgeBase implements:

- **ForgeProcess**: Defines **what** to do (intent, YAML specs, behaviors)
- **ForgeBase**: Implements **how** to do it (code, execution, infrastructure)

For the Forge Framework to be truly **cognitive**, there must be a **feedback loop** between intent (ForgeProcess) and execution (ForgeBase):

```
┌──────────────────────────────────────────────────┐
│                                                  │
│  ForgeProcess (Intent Layer)                    │
│  - Defines YAML specs                           │
│  - Captures intents                             │
│  - Orchestrates processes                       │
│                                                  │
└────────────────┬─────────────────────────────────┘
                 │
                 │ YAML Specs
                 ▼
         ┌───────────────┐
         │  YAML ↔ Code  │  ← Bidirectional Sync
         │      Sync      │
         └───────┬───────┘
                 │
                 │ Generated Code / Validation
                 ▼
┌──────────────────────────────────────────────────┐
│                                                  │
│  ForgeBase (Execution Layer)                    │
│  - Executes UseCases                            │
│  - Validates business rules                     │
│  - Collects metrics                             │
│                                                  │
└────────────────┬─────────────────────────────────┘
                 │
                 │ Execution Data
                 ▼
         ┌───────────────┐
         │ Intent Tracker │  ← Coherence Validation
         │ & Feedback     │
         └───────┬───────┘
                 │
                 │ Learning Data
                 ▼
┌──────────────────────────────────────────────────┐
│                                                  │
│  ForgeProcess (Learning)                        │
│  - Analyzes coherence                           │
│  - Adjusts processes                            │
│  - Improves specifications                      │
│                                                  │
└──────────────────────────────────────────────────┘
```

### Challenges

1. **Drift Detection**: How to detect when code no longer reflects the YAML spec?
2. **Bidirectional Sync**: How to keep YAML and code synchronized?
3. **Coherence Validation**: How to measure whether execution fulfilled the intent?
4. **Learning Loop**: How does execution feedback improve specifications?
5. **Autonomy**: How to prevent ForgeBase from depending on ForgeProcess at runtime?

### Forces at Play

**Needs:**
- Automatic YAML ↔ Code synchronization
- Cognitive coherence validation
- Feedback loop for learning
- Code generation from specs
- Divergence detection

**Risks:**
- Excessive coupling
- Synchronization overhead
- Maintenance complexity
- Merge conflicts (YAML vs Code)

## Decision

**We adopted bidirectional integration with two main components: YAMLSync and IntentTracker.**

### 1. YAMLSync: YAML ↔ Code Synchronization

**Purpose**: Keep YAML specifications and Python code synchronized.

#### YAML Schema for UseCases

```yaml
# specs/create_user.yaml
version: "1.0"
usecase:
  name: CreateUser
  description: Create a new user in the system

  inputs:
    - name: name
      type: str
      required: true
      validation:
        - not_empty
        - max_length: 100

    - name: email
      type: str
      required: true
      validation:
        - email_format
        - unique

  outputs:
    - name: user_id
      type: str
      description: Unique identifier of created user

    - name: name
      type: str

    - name: email
      type: str

  business_rules:
    - Email must be unique in the system
    - Name cannot be empty
    - Email must be valid format
    - User is created as active by default

  errors:
    - code: USER_EMAIL_DUPLICATE
      message: "User with email '{email}' already exists"

    - code: USER_INVALID_EMAIL
      message: "Invalid email format: '{email}'"
```

#### YAMLSync Features

**1. Parse YAML → Validation**
```python
sync = YAMLSync()
spec = sync.parse_yaml("specs/create_user.yaml")
# Validates schema version, required fields, etc.
```

**2. Generate Code from YAML**
```python
code = sync.generate_code(spec)
# Generates:
# - Input DTO (CreateUserInput)
# - Output DTO (CreateUserOutput)
# - UseCase skeleton (CreateUserUseCase)
# - Docstrings with business rules
```

**Generated code:**
```python
class CreateUserInput(DTOBase):
    """Input DTO for CreateUser."""

    def __init__(self, name: str, email: str):
        self.name = name
        self.email = email

    def validate(self) -> None:
        if not self.name:
            raise ValidationError("Name cannot be empty")
        if len(self.name) > 100:
            raise ValidationError("Name too long (max 100 chars)")
        if not self._is_valid_email(self.email):
            raise ValidationError(f"Invalid email format: {self.email}")

class CreateUserOutput(DTOBase):
    """Output DTO for CreateUser."""

    def __init__(self, user_id: str, name: str, email: str):
        self.user_id = user_id
        self.name = name
        self.email = email

class CreateUserUseCase(UseCaseBase):
    """
    Create a new user in the system.

    Business Rules:
        - Email must be unique in the system
        - Name cannot be empty
        - Email must be valid format
        - User is created as active by default
    """

    def execute(self, input_dto: CreateUserInput) -> CreateUserOutput:
        # TODO: Implement business logic
        raise NotImplementedError()
```

**3. Detect Drift (Validate Code against YAML)**
```python
drift = sync.detect_drift(CreateUserUseCase, spec)

if drift:
    for issue in drift:
        print(f"⚠️  {issue}")
    # Outputs:
    # ⚠️  Class name mismatch: expected CreateUser, got CreateUserUseCase
    # ⚠️  Missing business rule: Email must be unique
    # ⚠️  Description mismatch in docstring
```

**4. Export Code → YAML**
```python
sync.export_to_yaml(CreateUserUseCase, "specs/create_user_exported.yaml")
# Reverse engineering: Code → YAML
```

#### Development Workflow

**Option A: YAML-First (Recommended)**
```bash
# 1. Create YAML spec
vim specs/create_user.yaml

# 2. Generate code skeleton
forge_base generate usecase specs/create_user.yaml

# 3. Implement logic
vim src/application/create_user_usecase.py

# 4. Validate consistency
forge_base validate usecase CreateUserUseCase --spec specs/create_user.yaml
```

**Option B: Code-First**
```bash
# 1. Implement UseCase
vim src/application/create_user_usecase.py

# 2. Export to YAML
forge_base export usecase CreateUserUseCase --output specs/create_user.yaml

# 3. Refine YAML in ForgeProcess
```

#### CI/CD Integration

```yaml
# .github/workflows/validate.yml
- name: Validate YAML ↔ Code Sync
  run: |
    forge_base validate all-usecases --fail-on-drift
    # Fails if any UseCase has drift
```

### 2. IntentTracker: Cognitive Coherence

**Purpose**: Validate that execution fulfills the original intent.

#### Intent Tracking Flow

**1. Capture Intent (ForgeProcess)**
```python
# Before executing
intent_id = intent_tracker.capture_intent(
    description="Create user with name Alice and email alice@example.com",
    expected_outcome="User created successfully with valid email",
    source="forgeprocess",
    context={
        "workflow_id": "wf-123",
        "step": "create_user"
    }
)
```

**2. Execute (ForgeBase)**
```python
# Normal execution
result = usecase.execute(CreateUserInput(
    name="Alice",
    email="alice@example.com"
))
```

**3. Record Execution**
```python
# After execution
intent_tracker.record_execution(
    intent_id=intent_id,
    actual_outcome=f"User {result.user_id} created with email {result.email}",
    success=True,
    duration_ms=42.5,
    artifacts={
        "user_id": result.user_id,
        "email": result.email
    }
)
```

**4. Validate Coherence**
```python
# Coherence analysis
report = intent_tracker.validate_coherence(intent_id)

print(f"Coherence Level: {report.coherence_level.value}")
# Output: "perfect" (≥95% similarity)

print(f"Similarity: {report.similarity_score:.2%}")
# Output: 96.50%

print(f"Matches: {report.matches}")
# Output: ['user', 'created', 'email', 'alice@example.com']

if report.divergences:
    print(f"Divergences: {report.divergences}")

if report.recommendations:
    print("Recommendations:")
    for rec in report.recommendations:
        print(f"  - {rec}")
```

#### Coherence Levels

```python
class CoherenceLevel(Enum):
    PERFECT = "perfect"      # ≥95% similarity
    HIGH = "high"            # 80-94%
    MEDIUM = "medium"        # 60-79%
    LOW = "low"              # 40-59%
    DIVERGENT = "divergent"  # <40%
```

#### Learning Data Export

```python
# Export data for ML analysis
learning_data = intent_tracker.export_learning_data()

# Format:
[
  {
    "intent": {
      "id": "intent-123",
      "description": "Create user...",
      "expected_outcome": "User created...",
      "timestamp": 1699000000.0
    },
    "execution": {
      "actual_outcome": "User abc-123 created...",
      "success": true,
      "duration_ms": 42.5,
      "artifacts": {...}
    },
    "coherence": {
      "level": "perfect",
      "similarity_score": 0.965,
      "matches": [...],
      "divergences": []
    }
  },
  ...
]

# Save for analysis
with open("/var/learning/coherence_data.jsonl", "w") as f:
    for record in learning_data:
        f.write(json.dumps(record) + "\n")
```

### 3. Feedback Manager

**Purpose**: Orchestrate feedback from ForgeBase → ForgeProcess.

```python
# src/forge_base/observability/feedback_manager.py
class FeedbackManager:
    """
    Manages feedback loops between ForgeBase and ForgeProcess.

    Collects:
    - Intent tracking data
    - Execution metrics
    - Coherence reports
    - Performance data
    """

    def collect_feedback(
        self,
        usecase_name: str,
        intent_id: str
    ) -> FeedbackReport:
        """Collect comprehensive feedback for a UseCase execution."""

        # Intent data
        intent = self.intent_tracker.get_intent(intent_id)
        execution = self.intent_tracker.get_execution(intent_id)
        coherence = self.intent_tracker.validate_coherence(intent_id)

        # Metrics
        metrics = self.metrics_collector.get_metrics(
            usecase=usecase_name,
            correlation_id=intent_id
        )

        # Logs
        logs = self.log_service.query(correlation_id=intent_id)

        return FeedbackReport(
            intent=intent,
            execution=execution,
            coherence=coherence,
            metrics=metrics,
            logs=logs,
            recommendations=self._generate_recommendations(...)
        )

    def export_to_forgeprocess(self, report: FeedbackReport):
        """Export feedback to ForgeProcess for learning."""
        # Write to shared storage
        # Or send via API
        # Or publish to message queue
        ...
```

### 4. Autonomy: Runtime Independence

**Critical Principle**: ForgeBase **does not depend** on ForgeProcess at runtime.

```python
# ✅ ForgeBase works standalone
core = ForgeBaseCore()
usecase = core.get_usecase(CreateUserUseCase)
result = usecase.execute(input_dto)
# Without ForgeProcess, without YAML, works perfectly

# ✅ With ForgeProcess, adds feedback
intent_id = intent_tracker.capture_intent(...)  # Optional
result = usecase.execute(input_dto)
intent_tracker.record_execution(intent_id, ...)  # Optional
```

**Autonomy guaranteed by:**
- YAMLSync is a **build-time tool**, not a runtime dependency
- IntentTracker is **optional** (can be disabled)
- ForgeBase can be distributed without ForgeProcess
- YAML specs are documentation, not requirements

## Consequences

### Positive

✅ **Automatic Synchronization**
```bash
# Generate code
forge_base generate usecase specs/create_user.yaml

# Validate consistency
forge_base validate usecase CreateUserUseCase
```

✅ **Quantitatively Validated Coherence**
```python
report = intent_tracker.validate_coherence(intent_id)
assert report.similarity_score >= 0.80
```

✅ **Learning Loop**
```python
# Automatic feedback for ForgeProcess
learning_data = intent_tracker.export_learning_data()
# ForgeProcess uses it to improve specs
```

✅ **Living Documentation**
```yaml
# YAML serves as always up-to-date documentation
# Drift detection ensures code reflects the spec
```

✅ **Intent-Driven Development**
```bash
# 1. Spec defines intent (ForgeProcess)
# 2. Code implements (ForgeBase)
# 3. Tests validate coherence
# 4. Feedback improves spec
# 5. Repeat
```

### Negative

⚠️ **Synchronization Overhead**
- Keeping YAML and code synchronized requires discipline
- Drift can occur if validation is not in CI

**Mitigation**: Automatic validation in CI/CD

⚠️ **Tooling Complexity**
- YAMLSync and IntentTracker add complexity
- Learning curve

**Mitigation**: Clear docs, examples, sensible defaults

⚠️ **Learning Data Storage**
- Learning data can grow
- Requires storage and processing

**Mitigation**: Retention policies, aggregation

⚠️ **Tracking Latency**
- Intent tracking adds ~1-5ms per execution

**Mitigation**: Optional, can be disabled in prod

### Implemented Mitigations

1. **Runtime Autonomy**
   - ForgeBase works without ForgeProcess
   - Intent tracking is optional
   - Zero runtime dependencies

2. **Ergonomic Tooling**
   - CLI commands: `generate`, `validate`, `export`
   - IDE integration (future)
   - Auto-completion

3. **Sensible Defaults**
   - Intent tracking disabled by default in prod
   - Configurable sampling
   - Minimal performance overhead

## Alternatives Considered

### 1. Tight Coupling (Runtime Dependency)

```python
# ForgeBase depends on ForgeProcess at runtime
class CreateUserUseCase:
    def execute(self, input_dto):
        spec = ForgeProcess.get_spec("CreateUser")  # Runtime call
        ...
```

**Rejected because:**
- Violation of autonomy
- ForgeBase cannot work standalone
- Performance overhead
- Unnecessary coupling

### 2. Code-Only (No YAML)

**Rejected because:**
- Loses declarative specification
- No feedback loop for ForgeProcess
- Code is source of truth (hard for non-devs)

### 3. YAML-Only (Generated Code Never Edited)

**Rejected because:**
- Generated code is always limited
- Developers need flexibility
- Complexity moves to YAML (worse)

### 4. No Coherence Validation

**Rejected because:**
- Misses learning opportunity
- No quantitative feedback
- "It works" is not the same as "It works as intended"

## Implementation Guidelines

### For Developers

**Recommended workflow:**

1. **Define YAML Spec** (with ForgeProcess)
   ```yaml
   # specs/my_usecase.yaml
   usecase:
     name: MyUseCase
     ...
   ```

2. **Generate Skeleton**
   ```bash
   forge_base generate usecase specs/my_usecase.yaml
   ```

3. **Implement Logic**
   ```python
   # Edit generated code
   class MyUseCaseUseCase(UseCaseBase):
       def execute(self, input_dto):
           # Real implementation
           ...
   ```

4. **Validate Consistency**
   ```bash
   forge_base validate usecase MyUseCase --spec specs/my_usecase.yaml
   ```

5. **Tests with Intent Tracking**
   ```python
   def test_my_usecase():
       intent_id = tracker.capture_intent(...)
       result = usecase.execute(input_dto)
       tracker.record_execution(intent_id, ...)

       report = tracker.validate_coherence(intent_id)
       assert report.coherence_level in [CoherenceLevel.PERFECT, CoherenceLevel.HIGH]
   ```

### For Operators

**Configuration:**
```yaml
# config.yaml
integration:
  forgeprocess:
    intent_tracking:
      enabled: true  # false in prod for performance
      sampling_rate: 0.1  # 10%

    yaml_sync:
      validate_on_startup: true
      fail_on_drift: false  # warn only

    learning_export:
      enabled: true
      path: /var/learning/data.jsonl
      rotation: daily
```

## References

- **Behavior-Driven Development** by specification
- **Domain-Specific Languages** by Martin Fowler
- **Model-Driven Architecture** (MDA)
- **ForgeProcess Complete Documentation**: [docs/FORGE_PROCESS.md](../FORGE_PROCESS.md)
- YAML specification: https://yaml.org/spec/

## Related ADRs

- [ADR-001: Clean Architecture Choice](001-clean-architecture-choice.md)
- [ADR-003: Observability First](003-observability-first.md)
- [ADR-004: Cognitive Testing](004-cognitive-testing.md)

## Complete ForgeProcess Documentation

To understand the **complete cognitive cycle** (MDD → BDD → TDD → CLI → Feedback), see:

**[docs/FORGE_PROCESS.md](../FORGE_PROCESS.md)**

This ADR documents the **technical integration** (YAMLSync, IntentTracker, FeedbackManager).
The complete document explains the **philosophical and architectural context** of all 5 phases.

---

**Author:** ForgeBase Development Team
**Date:** 2025-11-03
**Updated:** 2025-11-04
**Version:** 1.1
