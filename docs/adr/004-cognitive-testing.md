# ADR-004: Cognitive Testing

## Status

**Accepted** (2025-11-03)

## Context

ForgeBase is not just a technical framework, it is a **cognitive** framework — code that thinks, measures, and explains. Traditional tests validate **behavior** ("does the code do what it should do?"), but do not validate **intent** ("does the code do what we INTENDED it to do?").

### Limitations of Traditional Tests

**Conventional Unit Tests:**
```python
def test_create_user():
    user = create_user("Alice", "alice@example.com")
    assert user.name == "Alice"
    assert user.email == "alice@example.com"
```

**What they validate:**
- ✅ Correct syntax
- ✅ Correct type
- ✅ Expected value

**What they DO NOT validate:**
- ❌ Was the original intent fulfilled?
- ❌ Coherence with specification (YAML/ForgeProcess)?
- ❌ Is instrumentation working?
- ❌ Unintended side effects?
- ❌ Acceptable performance?

### ForgeBase Needs

As a cognitive framework, we need to validate:

1. **Cognitive Coherence**: Intent vs Execution
2. **Observability**: Are metrics being collected?
3. **Purity**: Functions without unintended side effects?
4. **Performance**: Execution within acceptable limits?
5. **Traceability**: Are correlation IDs propagating?
6. **Feedback Loops**: Is learning data being generated?

### Forces at Play

**Needs:**
- Validate not just "it works", but "it works as INTENDED"
- Detect drift between specification and implementation
- Ensure observability is active
- Validate ForgeProcess ↔ ForgeBase integration

**Risks:**
- More complex tests to write
- Additional validation overhead
- Learning curve for new developers
- Potential for over-testing

## Decision

**We adopted "Cognitive Testing" as a testing philosophy: validate intent, not just behavior.**

### Concept: ForgeTestCase

We created `ForgeTestCase`, an extension of `unittest.TestCase` with **cognitive assertions**:

```python
class ForgeTestCase(unittest.TestCase):
    """
    Base class for cognitive tests.

    Adds validations for:
    - Intent vs execution
    - Collected metrics
    - Functional purity
    - Performance
    """

    def assert_intent_matches(self, expected: str, actual: str, threshold: float = 0.8)
    def assert_metrics_collected(self, metrics: dict)
    def assert_no_side_effects(self, fn: Callable)
    def assert_performance_within(self, fn: Callable, max_duration_ms: float)
```

### Cognitive Assertions

#### 1. assert_intent_matches

**Purpose**: Validate that the actual execution corresponds to the original intent.

```python
class TestCreateUser(ForgeTestCase):
    def test_creates_user_with_intent(self):
        # Capture intent
        intent = "Create a new user with valid email address"

        # Execution
        result = usecase.execute(CreateUserInput(
            name="Alice",
            email="alice@example.com"
        ))

        # Cognitive validation
        actual = f"Created user {result.user_id} with email {result.email}"

        self.assert_intent_matches(
            expected=intent,
            actual=actual,
            threshold=0.8  # 80% minimum similarity
        )
```

**Implementation:**
- Uses similarity analysis (difflib.SequenceMatcher)
- Configurable threshold
- Descriptive message on failure

#### 2. assert_metrics_collected

**Purpose**: Ensure that metrics are being collected.

```python
class TestCreateUser(ForgeTestCase):
    def test_collects_metrics(self):
        fake_metrics = FakeMetricsCollector()
        usecase = CreateUserUseCase(
            user_repository=fake_repo,
            metrics_collector=fake_metrics
        )

        usecase.execute(input_dto)

        # Validate that expected metrics were collected
        self.assert_metrics_collected({
            'create_user.duration': lambda v: v > 0,
            'create_user.count': lambda v: v == 1,
            'create_user.success': lambda v: v == True
        })
```

**Implementation:**
- Checks metric presence
- Validates values with predicates
- Descriptive failure showing missing metrics

#### 3. assert_no_side_effects

**Purpose**: Validate functional purity (absence of side effects).

```python
class TestEmailValueObject(ForgeTestCase):
    def test_validation_has_no_side_effects(self):
        email = Email("alice@example.com")

        # Validate that multiple calls don't change state
        self.assert_no_side_effects(
            lambda: email.validate()
        )

        # Email should be immutable after creation
        with self.assertRaises(AttributeError):
            email.address = "bob@example.com"
```

**Implementation:**
- Executes function multiple times
- Checks state before and after
- Detects unwanted mutations

#### 4. assert_performance_within

**Purpose**: Ensure acceptable performance.

```python
class TestCreateUser(ForgeTestCase):
    def test_executes_within_acceptable_time(self):
        # Should execute in less than 50ms
        self.assert_performance_within(
            lambda: usecase.execute(input_dto),
            max_duration_ms=50.0
        )
```

**Implementation:**
- Measures execution time
- Fails if it exceeds the threshold
- Shows actual vs expected duration

### Structure of a Cognitive Test

```python
class TestCreateUserUseCase(ForgeTestCase):
    def setUp(self):
        """Setup with fakes and context."""
        self.fake_repo = FakeRepository()
        self.fake_metrics = FakeMetricsCollector()
        self.fake_logger = FakeLogger()

        self.usecase = CreateUserUseCase(
            user_repository=self.fake_repo,
            metrics_collector=self.fake_metrics,
            logger=self.fake_logger
        )

    def test_creates_user_cognitive_validation(self):
        """
        Complete cognitive test:
        - Validates behavior
        - Validates intent
        - Validates metrics
        - Validates performance
        """
        # 1. Capture intent
        intent = "Create user with name Alice and email alice@example.com"

        # 2. Execution
        result = self.usecase.execute(CreateUserInput(
            name="Alice",
            email="alice@example.com"
        ))

        # 3. Traditional validations
        self.assertEqual(result.name, "Alice")
        self.assertEqual(result.email, "alice@example.com")
        self.assertTrue(result.user_id)

        # 4. Cognitive validations

        # 4a. Intent coherence
        self.assert_intent_matches(
            expected=intent,
            actual=f"Created user {result.name} with email {result.email}"
        )

        # 4b. Metrics collected
        self.assert_metrics_collected({
            'create_user.duration': lambda v: v > 0,
            'create_user.count': lambda v: v == 1
        })

        # 4c. Structured logs
        logs = self.fake_logger.get_logs(level='info')
        self.assertTrue(any('user_created' in log['message'] for log in logs))
        self.assertTrue(any('user_id' in log['context'] for log in logs))

        # 4d. Performance
        self.assert_performance_within(
            lambda: self.usecase.execute(input_dto),
            max_duration_ms=100.0
        )

        # 4e. Side effects (repository state)
        self.assertEqual(self.fake_repo.count(), 1)
        self.assertTrue(self.fake_repo.exists(result.user_id))
```

### Cognitive Test Doubles

ForgeBase provides specialized fakes for cognitive tests:

#### FakeLogger
```python
class FakeLogger(LoggerPort):
    """In-memory logger for tests."""

    def get_logs(self, level: str = None) -> List[dict]:
        """Returns collected logs."""

    def assert_logged(self, message: str, level: str = 'info'):
        """Assert that a message was logged."""

    def assert_context_present(self, **context):
        """Assert that context is present in some log."""
```

#### FakeMetricsCollector
```python
class FakeMetricsCollector:
    """In-memory metrics collector."""

    def get_metric(self, name: str) -> Optional[Metric]:
        """Returns collected metric."""

    def assert_metric_collected(self, name: str, predicate: Callable):
        """Assert on metric value."""

    def get_all_metrics(self) -> dict:
        """Returns all collected metrics."""
```

#### FakeRepository
```python
class FakeRepository(RepositoryBase[T]):
    """In-memory repository for tests."""

    def count(self) -> int:
        """Number of entities."""

    def contains(self, id: str) -> bool:
        """Whether it contains the entity."""

    def get_all(self) -> List[T]:
        """All entities."""
```

### YAML ↔ Code Coherence Tests

To validate ForgeProcess synchronization:

```python
class TestYAMLCodeCoherence(ForgeTestCase):
    def test_usecase_matches_yaml_spec(self):
        """Validate that code implements the YAML spec."""
        # Load YAML spec
        sync = YAMLSync()
        spec = sync.parse_yaml("specs/create_user.yaml")

        # Detect drift
        drift = sync.detect_drift(CreateUserUseCase, spec)

        # Should have zero drift
        self.assertEqual(len(drift), 0,
            f"Drift detected between YAML and code: {drift}")

    def test_generated_code_matches_manual_implementation(self):
        """Validate that generated code would be identical to manual."""
        spec = sync.parse_yaml("specs/create_user.yaml")
        generated = sync.generate_code(spec)

        # Parse both and compare AST
        # (simplified implementation)
        self.assertCodeStructureMatches(generated, CreateUserUseCase)
```

### Intent Tracking Tests

```python
class TestIntentTracking(ForgeTestCase):
    def test_tracks_intent_coherence(self):
        """Validate cognitive coherence tracking."""
        tracker = IntentTracker()

        # Capture intent
        intent_id = tracker.capture_intent(
            description="Create user",
            expected_outcome="User created successfully"
        )

        # Execute
        result = usecase.execute(input_dto)

        # Record execution
        tracker.record_execution(
            intent_id=intent_id,
            actual_outcome=result.message,
            success=True
        )

        # Validate coherence
        report = tracker.validate_coherence(intent_id)

        # Cognitive assertions
        self.assertIn(report.coherence_level, [
            CoherenceLevel.PERFECT,
            CoherenceLevel.HIGH
        ])
        self.assertGreaterEqual(report.similarity_score, 0.8)
        self.assertEqual(len(report.divergences), 0)
```

## Consequences

### Positive

✅ **Holistic Validation**
- Not just "it works", but "it works as intended"
- Detects drift between intent and implementation
- Ensures observability is active

✅ **Improved Debugging**
```python
# When a test fails, we have rich context:
AssertionError: Intent match failed
Expected: "Create user with email alice@example.com"
Actual: "User created with ID 123"
Similarity: 0.42 (below threshold 0.80)
Recommendation: Include email in success message for better coherence
```

✅ **Living Documentation**
- Tests document intent
- ForgeTestCase shows usage patterns
- Assertions explain cognitive contracts

✅ **Cognitive Regression**
- Detects when code "works but not as before"
- Prevents coherence degradation over time
- Maintains alignment with ForgeProcess

✅ **Confidence in Refactoring**
- Refactor without fear of breaking coherence
- Automatic intent validation
- Cognitive safety net

### Negative

⚠️ **Additional Complexity**
- More verbose tests
- Learning curve
- More test code

⚠️ **Maintenance Overhead**
- Update tests when intent changes
- Keep thresholds calibrated
- Review cognitive assertions

⚠️ **Potential for Flakiness**
- Similarity thresholds can be sensitive
- Performance tests may fail on slow CI
- Context-dependent validations

### Mitigations

1. **Tooling**
   - Cognitive test generators
   - Templates for common cases
   - Linters to validate patterns

2. **Sensible Defaults**
   - Thresholds calibrated by real usage
   - Timeouts adjusted for CI
   - Optimized fakes

3. **Documentation**
   - Cognitive testing cookbook
   - Examples for each pattern
   - ADR explaining philosophy

4. **Pragmatism**
   - Not every test needs to be cognitive
   - Cognitive tests for critical UseCases
   - Traditional unit tests for utilities

## Alternatives Considered

### 1. Traditional Tests Only

**Rejected because:**
- Does not validate intent
- Does not detect drift
- Does not verify observability
- Misses opportunity to validate coherence

### 2. Property-Based Testing (Hypothesis)

```python
@given(st.text(), st.emails())
def test_create_user(name, email):
    user = create_user(name, email)
    assert user.name == name
```

**Not rejected, but complementary:**
- Property-based tests are useful for edge cases
- Cognitive tests validate specific intent
- Both can coexist

### 3. Snapshot Testing

```python
def test_create_user():
    result = usecase.execute(input_dto)
    assert_snapshot_matches(result, "create_user_snapshot.json")
```

**Not rejected, but limited:**
- Snapshots validate structure, not intent
- Useful for format regression
- Cognitive tests validate semantics

### 4. Contract Testing (Pact)

**Not rejected, but different scope:**
- Pact validates contracts between services
- Cognitive tests validate intent within a service
- Complementary, not mutually exclusive

## Implementation Guidelines

### When to Use Cognitive Tests

**Use for:**
- ✅ Critical business UseCases
- ✅ Code that changes frequently
- ✅ ForgeProcess ↔ ForgeBase integration
- ✅ Observability validation
- ✅ Performance-critical paths

**Do not use for:**
- ❌ Simple utilities (use traditional unit tests)
- ❌ Third-party libraries
- ❌ One-off scripts
- ❌ Purely technical code without intent

### Recommended Structure

```
tests/
├── unit/                       # Traditional unit tests
│   ├── test_entity_base.py
│   └── test_value_object.py
├── integration/                # Integration tests
│   └── test_repository_sql.py
└── cognitive/                  # Cognitive tests
    ├── test_create_user_cognitive.py
    ├── test_yaml_sync_coherence.py
    └── test_intent_tracking.py
```

## References

- **Growing Object-Oriented Software, Guided by Tests** by Freeman & Pryce
- **Test-Driven Development** by Kent Beck
- **Property-Based Testing** by David MacIver
- ForgeBase testing examples: `tests/unit/testing/`

## Related ADRs

- [ADR-003: Observability First](003-observability-first.md)
- [ADR-006: ForgeProcess Integration](006-forgeprocess-integration.md)

---

**Author:** ForgeBase Development Team
**Date:** 2025-11-03
**Version:** 1.0
