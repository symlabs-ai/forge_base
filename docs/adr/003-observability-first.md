# ADR-003: Observability First

## Status

**Accepted** (2025-11-03)

## Context

ForgeBase was designed to be a **cognitive** framework — it does not just execute code, but **understands, measures, and explains** its own behavior. For this, observability cannot be an afterthought "add-on", but rather a **native characteristic** of the architecture.

### Challenges of Traditional Systems

In traditional systems, observability is frequently:
- **Added later**: "We'll add logs when something breaks"
- **Inconsistent**: Some modules log, others don't
- **Superficial**: Logs without context, metrics without meaning
- **Expensive**: Manual instrumentation overhead
- **Fragmented**: Logs here, metrics there, traces somewhere else

### ForgeBase Needs

As a cognitive framework, ForgeBase needs:

1. **Self-Reflection**: Ability to introspect its own behavior
2. **Traceability**: Understanding the journey of each execution
3. **Continuous Measurement**: Performance, success, and coherence metrics
4. **Cognitive Debugging**: Not just "where it failed", but "why it failed"
5. **Feedback Loops**: Data for continuous learning
6. **Transparency**: Explaining decisions and executions

### Forces at Play

**Needs:**
- Efficient debugging in production
- Performance monitoring
- Cognitive coherence validation (intent vs execution)
- Feedback for ForgeProcess
- Decision auditing

**Risks:**
- Performance overhead
- Storage cost (logs, metrics)
- Configuration complexity
- Information overload (signal vs noise)

## Decision

**We adopted "Observability First" as a fundamental principle: observability is native, not optional.**

### Observability Pillars

#### 1. Structured Logging (LogService)

**Decision**: All logs are structured (JSON), not strings.

```python
# ❌ Traditional (unstructured)
logger.info("User created: Alice")

# ✅ ForgeBase (structured)
logger.info(
    "User created",
    user_id="123",
    user_name="Alice",
    email="alice@example.com",
    duration_ms=42.5,
    correlation_id="abc-def"
)
```

**Benefits:**
- Queryable: Easily search by `user_id=123`
- Automatic context propagation
- Correlation IDs trace requests
- Machine-readable for analysis

**Implementation**:
- `src/forge_base/observability/log_service.py` (~489 LOC)
- Handlers: stdout, file, remote (Elasticsearch, CloudWatch)
- Levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Sampling for high-volume scenarios

#### 2. Active Metrics (TrackMetrics)

**Decision**: UseCases and Ports are automatically instrumented.

**Types of Metrics:**

```python
# Counters: Event counts
track_metrics.increment("usecase.execution.count", usecase="CreateUser")
track_metrics.increment("usecase.execution.errors", usecase="CreateUser")

# Gauges: Instantaneous values
track_metrics.gauge("system.memory.usage", value=512.5, unit="MB")

# Histograms: Value distributions
track_metrics.histogram("usecase.execution.duration", value=42.5, usecase="CreateUser")
```

**Standard Metrics (Auto-collected):**
- `usecase.execution.duration` — Execution time
- `usecase.execution.count` — Number of executions
- `usecase.execution.errors` — Number of errors
- `usecase.execution.success_rate` — Success rate
- `port.call.duration` — Port call duration
- `adapter.request.count` — Requests per adapter

**Implementation**:
- `src/forge_base/observability/track_metrics.py` (~447 LOC)
- Export formats: Prometheus, JSON, StatsD
- In-memory aggregation
- Overhead < 1ms per metric

#### 3. Distributed Tracing (TracerPort)

**Decision**: Native support for distributed tracing (OpenTelemetry-compatible).

**Concept**: Each execution creates a **trace** with multiple **spans**:

```
Trace: CreateUser (correlation_id: abc-123)
├─ Span: usecase.execute [42ms]
│  ├─ Span: domain.validate [2ms]
│  ├─ Span: repository.save [35ms]
│  └─ Span: logger.info [1ms]
└─ Span: adapter.respond [3ms]
```

**Implementation**:
- `src/forge_base/observability/tracer_port.py` (~504 LOC)
- OpenTelemetry-compatible interface
- Automatic context propagation
- Adapters: Jaeger, Zipkin, DataDog

#### 4. Cognitive Coherence (FeedbackManager + IntentTracker)

**Decision**: Track coherence between intent and execution.

**Flow:**
1. **Capture Intent** (before execution)
   ```python
   intent_id = tracker.capture_intent(
       description="Create user with valid email",
       expected_outcome="User created successfully"
   )
   ```

2. **Execute**
   ```python
   result = usecase.execute(input_dto)
   ```

3. **Record Execution** (after execution)
   ```python
   tracker.record_execution(
       intent_id=intent_id,
       actual_outcome=result.message,
       success=True,
       duration_ms=42.5
   )
   ```

4. **Validate Coherence**
   ```python
   report = tracker.validate_coherence(intent_id)
   # report.coherence_level: PERFECT, HIGH, MEDIUM, LOW, DIVERGENT
   # report.similarity_score: 0.0 - 1.0
   # report.recommendations: ["Improve error message clarity"]
   ```

**Implementation**:
- `src/forge_base/observability/feedback_manager.py` (~455 LOC)
- `src/forge_base/integration/intent_tracker.py` (~450 LOC)
- Similarity analysis using difflib
- Learning data export for ML

### Automatic Instrumentation

#### Decorator @track_metrics

**Decision**: UseCases can be instrumented with a decorator.

```python
from forge_base.application.decorators import track_metrics

class CreateUserUseCase(UseCaseBase):
    @track_metrics(
        metric_name="create_user",
        track_duration=True,
        track_errors=True
    )
    def execute(self, input_dto: CreateUserInput) -> CreateUserOutput:
        # Metrics collected automatically:
        # - create_user.duration
        # - create_user.count
        # - create_user.errors (if exception)
        ...
```

**Implementation**:
- `src/forge_base/application/decorators/track_metrics.py` (~283 LOC)
- Zero overhead when disabled
- Async-compatible
- Context propagation

### Observability Levels

ForgeBase supports 3 configurable levels:

**1. MINIMAL (Production)**
- Logs: ERROR, CRITICAL
- Metrics: Aggregated (1min resolution)
- Traces: 1% sampling (for performance)

**2. STANDARD (Staging)**
- Logs: INFO, WARNING, ERROR, CRITICAL
- Metrics: All
- Traces: 10% sampling

**3. DEBUG (Development)**
- Logs: ALL (DEBUG included)
- Metrics: All (real-time)
- Traces: 100% (all requests)

### Configuration

```yaml
# config.yaml
observability:
  level: standard  # minimal | standard | debug

  logging:
    handlers:
      - stdout
    - file: /var/log/forge_base.log
    format: json
    correlation_id: true

  metrics:
    enabled: true
    export:
      - prometheus: http://localhost:9090
      - json: /var/metrics/forge_base.json
    collection_interval: 60  # seconds

  tracing:
    enabled: true
    provider: jaeger
    endpoint: http://localhost:14268
    sampling_rate: 0.1  # 10%

  cognitive:
    intent_tracking: true
    coherence_validation: true
    learning_export: /var/learning/data.jsonl
```

## Consequences

### Positive

✅ **Efficient Debugging**
```python
# Find a specific execution by correlation_id
logs = log_service.query(correlation_id="abc-123")

# See the complete timeline of an execution
trace = tracer.get_trace("abc-123")

# Analyze coherence of an operation
report = intent_tracker.validate_coherence(intent_id)
```

✅ **Full Visibility**
- Know exactly what is happening in production
- Detect performance degradation before it becomes a problem
- Understand usage patterns

✅ **Cognitive Feedback Loop**
- Coherence data feeds ForgeProcess
- Continuous learning about execution quality
- Iterative improvement based on real data

✅ **Auditing & Compliance**
- Complete trail of operations
- Traceability of decisions
- Regulatory compliance

✅ **Performance Tuning**
- Easily identify bottlenecks
- Compare performance of different implementations
- A/B testing of optimizations

### Negative

⚠️ **Performance Overhead**
- Logging: ~0.1-0.5ms per log
- Metrics: ~0.1ms per metric
- Tracing: ~1-5ms per span
- **Mitigation**: Sampling, async logging, configurable levels

⚠️ **Storage Costs**
- Logs can grow rapidly
- Historical metrics require space
- Traces can be voluminous
- **Mitigation**: Retention policies, compression, aggregation

⚠️ **Operational Complexity**
- Observability infrastructure (Elasticsearch, Prometheus, Jaeger)
- Dashboards and alerting
- Technical knowledge required
- **Mitigation**: Sensible defaults, self-hosted options, clear docs

⚠️ **Signal vs Noise**
- Excessive logs can hinder debugging
- Too many metrics can be confusing
- Detailed traces can be overwhelming
- **Mitigation**: Configurable levels, smart sampling, filtering

### Implemented Mitigations

1. **Performance**
   - Asynchronous logging (does not block execution)
   - In-memory metrics aggregation
   - Configurable sampling for traces
   - Lazy context evaluation

2. **Storage**
   - Configurable retention policies
   - Automatic log rotation
   - Metrics downsampling (e.g., 1min → 1hour → 1day)
   - Log compression

3. **Usability**
   - Defaults work out-of-the-box
   - Can be completely disabled if needed
   - Fakes for tests (zero overhead)
   - Clear documentation

## Alternatives Considered

### 1. Optional Observability (Add-on)

```python
# Observability as an "extra"
class CreateUserUseCase:
    def execute(self, input_dto):
        # Pure logic, no instrumentation
        ...

# User adds observability manually
```

**Rejected because:**
- Inconsistency: Some UseCases instrumented, others not
- Forgetfulness: Easy to forget to add
- Overhead: Manual instrumentation is verbose
- Fragmentation: Each developer does it differently

### 2. Traditional Logging (Strings)

```python
logger.info(f"User {user_id} created at {timestamp}")
```

**Rejected because:**
- Not queryable
- Complex parsing
- No structured context
- Hard to analyze automatically

### 3. Metrics Only at Critical Points

**Rejected because:**
- Thin line between "critical" and "non-critical"
- Tendency to under-instrument
- Debugging becomes harder
- Better to have everything and filter than not to have it

### 4. Mandatory Commercial APM (DataDog, NewRelic)

**Rejected because:**
- Vendor lock-in
- High cost
- Mandatory external dependency
- We prefer open standards (OpenTelemetry)
- Solution: Support APMs as an *option*, not a requirement

## Implementation Notes

### For UseCase Developers

**Observability is automatic:**
```python
class MyUseCase(UseCaseBase):
    def execute(self, input_dto):
        # Logging and metrics are already active
        # Just focus on business logic
        ...
```

**To add specific context:**
```python
def execute(self, input_dto):
    self.logger.info(
        "Processing order",
        order_id=input_dto.order_id,
        customer_id=input_dto.customer_id
    )
    ...
```

### For Operators

**Minimal configuration:**
```yaml
observability:
  level: standard
```

**Optimized production:**
```yaml
observability:
  level: minimal
  logging:
    handlers: [file]
  metrics:
    collection_interval: 300
  tracing:
    sampling_rate: 0.01  # 1%
```

## References

- **The Three Pillars of Observability** (Logs, Metrics, Traces)
- **OpenTelemetry Specification**
- **Site Reliability Engineering** by Google
- **Distributed Tracing in Practice** by Austin Parker et al.

## Related ADRs

- [ADR-001: Clean Architecture Choice](001-clean-architecture-choice.md)
- [ADR-004: Cognitive Testing](004-cognitive-testing.md)
- [ADR-006: ForgeProcess Integration](006-forgeprocess-integration.md)

---

**Author:** ForgeBase Development Team
**Date:** 2025-11-03
**Version:** 1.0
