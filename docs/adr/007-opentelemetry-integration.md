# ADR-007: OpenTelemetry Integration (Optional)

## Status

**Accepted** (2025-11-05)

## Context

ForgeBase was designed with native observability from the start (see [ADR-003](003-observability-first.md)). Currently, the framework has:

1. **Custom implementations**:
   - `InMemoryTracer` — tracing for dev/tests
   - `NoOpTracer` — zero overhead in production
   - `StdoutLogger` — structured JSON logging
   - `TrackMetrics` — in-memory metrics collection

2. **OpenTelemetry-compatible abstractions**:
   - `TracerPort` — OTel-compatible interface
   - `LoggerPort` — structured logging support
   - W3C Trace Context format support

3. **Zero mandatory dependencies** (only `pyyaml`)

### Emerging Needs

As ForgeBase is used in more complex production environments, new needs arise:

**1. Integration with Existing Infrastructure**
- Companies already use Jaeger, Zipkin, Prometheus, Grafana
- Commercial APMs (DataDog, New Relic, Dynatrace)
- SIEM systems that expect OTel/OTLP format

**2. Auto-Instrumentation**
- Automatically trace: HTTP requests, SQL queries, Redis calls, Kafka messages
- Without the need to manually instrument each library

**3. Automatic Correlation**
- Automatic correlation between logs, metrics, and traces
- Trace context propagation between microservices
- Baggage propagation for cross-service context

**4. Battle-Tested Exporters**
- Community-maintained exporters for 20+ backends
- Optimized protocols (OTLP, gRPC, HTTP/protobuf)
- Retry logic, buffering, batching already implemented

**5. Semantic Conventions**
- Consistent naming following industry standards
- Standardized attributes (`http.method`, `db.system`, etc.)
- Compatibility with analysis tools

### Forces at Play

**Needs:**
- ✅ Integration with existing observability infrastructure
- ✅ Auto-instrumentation of popular libraries
- ✅ Exporters for 20+ backends (Jaeger, Prometheus, etc.)
- ✅ Automatic logs+metrics+traces correlation
- ✅ Industry standards (W3C, OTel semantic conventions)
- ✅ Rich and battle-tested ecosystem

**Risks:**
- ⚠️ Heavy dependencies (~10+ packages)
- ⚠️ Configuration complexity
- ⚠️ Performance overhead (small but measurable)
- ⚠️ Learning curve
- ⚠️ Potential vendor lock-in if poorly implemented
- ⚠️ Losing the "lightweight by default" simplicity

**Constraints:**
- **Must not** break the "zero mandatory deps" philosophy
- **Must not** make OTel mandatory
- Unique cognitive system (FeedbackManager, IntentTracker) must be preserved
- Lightweight implementations must remain the default

## Decision

**We adopted OpenTelemetry as an OPTIONAL integration option, not mandatory.**

### Integration Principles

1. **Opt-In, Not Mandatory**
   - OTel is installed via `pip install forge_base[otel]`
   - User without OTel: works perfectly with builtin implementations
   - User with OTel: activates via configuration

2. **Adapter Pattern**
   - OTel implements existing interfaces (`TracerPort`, `LoggerPort`)
   - Does not break current abstractions
   - Interchangeable via configuration

3. **Lightweight by Default**
   - Standard installation: zero OTel deps
   - Dev/tests: InMemoryTracer, FakeLogger
   - Simple production: StdoutLogger, NoOpTracer
   - Complex production: OtelTracer, OtelLogger

4. **Preserve Cognitive System**
   - `FeedbackManager` and `IntentTracker` remain unique
   - They can INTEGRATE with OTel (create spans) but are not replaced
   - The cognitive system is a competitive differentiator

### Integration Architecture

```
src/forge_base/observability/
├── tracer_port.py           # Abstract interface (already exists)
├── logger_port.py           # Abstract interface (already exists)
├── track_metrics.py         # Builtin implementation (already exists)
│
└── otel/                    # New module (optional)
    ├── __init__.py
    ├── otel_tracer.py       # Implements TracerPort via OTel
    ├── otel_logger.py       # Implements LoggerPort via OTel
    ├── otel_metrics.py      # Implements TrackMetrics via OTel
    ├── auto_instrument.py   # Auto-instrumentation for libs
    └── providers.py         # TracerProvider setup, etc.
```

### Declarative Configuration

```yaml
# config-lightweight.yaml (default)
observability:
  level: standard

  tracing:
    provider: inmemory     # InMemoryTracer (builtin)

  logging:
    provider: stdout       # StdoutLogger (builtin)

  metrics:
    provider: builtin      # TrackMetrics (builtin)

---

# config-otel.yaml (optional)
observability:
  level: standard

  tracing:
    provider: opentelemetry
    config:
      service_name: forge_base-api
      exporter: jaeger
      endpoint: http://localhost:14268/api/traces
      sampling_rate: 0.1  # 10%

  logging:
    provider: opentelemetry
    config:
      exporter: otlp
      endpoint: http://localhost:4317

  metrics:
    provider: opentelemetry
    config:
      exporter: prometheus
      endpoint: http://localhost:9090
      interval: 60  # seconds

  # Auto-instrumentation (optional)
  auto_instrument:
    - requests      # HTTP client
    - sqlalchemy    # Database
    - redis         # Cache
    - flask         # Web framework
```

### Adapter Implementation

#### OtelTracer (implements TracerPort)

```python
# src/forge_base/observability/otel/otel_tracer.py

from forge_base.observability.tracer_port import TracerPort, Span, SpanKind, SpanStatus

try:
    from opentelemetry import trace
    from opentelemetry.trace import Status, StatusCode
    HAS_OTEL = True
except ImportError:
    HAS_OTEL = False


class OtelTracer(TracerPort):
    """
    OpenTelemetry implementation of TracerPort.

    This adapter bridges ForgeBase's tracing abstraction with the
    OpenTelemetry SDK, enabling export to any OTel-compatible backend
    (Jaeger, Zipkin, Tempo, DataDog, etc.).

    **Optional dependency**: Install with `pip install forge_base[otel]`

    Why this exists:
    - Enterprises already have OTel infrastructure
    - Auto-instrumentation of popular libraries (requests, sqlalchemy, etc.)
    - Battle-tested exporters for 20+ backends
    - Semantic conventions for consistency

    Design decisions:
    - Lazy import: OTel is optional, not required
    - Adapter pattern: implements TracerPort interface
    - Wraps OTel spans to ForgeBase Span objects

    :param service_name: Name of the service (for grouping)
    :type service_name: str
    :param config: OTel-specific configuration
    :type config: dict

    Example::

        >>> tracer = OtelTracer(service_name="my-api")
        >>> with tracer.span("database_query") as span:
        ...     span.set_attribute("query", "SELECT * FROM users")
        ...     result = db.query()
    """

    def __init__(self, service_name: str, config: Optional[dict] = None):
        if not HAS_OTEL:
            raise ImportError(
                "OpenTelemetry not installed. "
                "Install with: pip install forge_base[otel]"
            )

        self._service_name = service_name
        self._config = config or {}
        self._tracer = trace.get_tracer(service_name)

    def start_span(self, name: str, kind: SpanKind = SpanKind.INTERNAL,
                   **attributes) -> Span:
        """Start a new span using OTel."""
        otel_kind = self._convert_span_kind(kind)
        otel_span = self._tracer.start_span(name, kind=otel_kind)

        # Set attributes
        for key, value in attributes.items():
            otel_span.set_attribute(key, value)

        # Wrap OTel span in ForgeBase Span
        return self._wrap_otel_span(otel_span)

    def _wrap_otel_span(self, otel_span) -> Span:
        """Wrap OTel span to ForgeBase Span interface."""
        ctx = otel_span.get_span_context()

        return Span(
            span_id=format(ctx.span_id, '016x'),
            trace_id=format(ctx.trace_id, '032x'),
            name=otel_span.name,
            kind=self._convert_span_kind_back(otel_span.kind),
            # ... bridge other fields
        )

    # ... implementation details
```

#### Auto-Instrumentation

```python
# src/forge_base/observability/otel/auto_instrument.py

def auto_instrument(config: dict) -> None:
    """
    Auto-instrument popular libraries for automatic tracing.

    This function activates OpenTelemetry instrumentation for common
    Python libraries, enabling automatic span creation without manual
    instrumentation.

    Supported libraries:
    - requests, httpx, aiohttp (HTTP clients)
    - flask, fastapi, django (web frameworks)
    - sqlalchemy, psycopg2, pymysql (databases)
    - redis, celery (async/messaging)
    - boto3 (AWS SDK)

    Why this is valuable:
    - Zero code changes needed
    - Consistent instrumentation
    - Community-maintained

    :param config: Dict with library names as keys, True to enable
    :type config: dict

    Example::

        >>> auto_instrument({
        ...     "requests": True,
        ...     "sqlalchemy": True,
        ...     "redis": True
        ... })
    """

    if config.get("requests"):
        from opentelemetry.instrumentation.requests import RequestsInstrumentor
        RequestsInstrumentor().instrument()

    if config.get("sqlalchemy"):
        from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
        SQLAlchemyInstrumentor().instrument()

    if config.get("redis"):
        from opentelemetry.instrumentation.redis import RedisInstrumentor
        RedisInstrumentor().instrument()

    if config.get("flask"):
        from opentelemetry.instrumentation.flask import FlaskInstrumentor
        FlaskInstrumentor().instrument()

    # ... more instrumentations
```

### Integration with the Cognitive System

FeedbackManager and IntentTracker **integrate** with OTel but are not replaced:

```python
# src/forge_base/observability/feedback_manager.py

class FeedbackManager:
    def __init__(self, tracer: TracerPort):
        self._tracer = tracer  # Can be OtelTracer or InMemoryTracer

    def capture_intent(self, description: str, **context):
        """Capture intent and create trace span."""

        # Create span (works with any TracerPort implementation)
        with self._tracer.span("cognitive.capture_intent") as span:
            span.set_attribute("intent.description", description)
            span.set_attribute("intent.source", "forgeprocess")

            # Unique ForgeBase cognitive logic
            intent_record = self._create_intent_record(description, context)

            # If using OTel, this span will be exported to Jaeger/etc
            # If using InMemory, it stays in memory for tests

            return intent_record
```

**Differentiator:** The cognitive system creates special spans with unique semantics:
- `cognitive.capture_intent`
- `cognitive.validate_coherence`
- `cognitive.feedback_loop`

These do not exist in standard OTel — they are ForgeBase innovations.

### Installation and Setup

#### Standard Installation (Lightweight)
```bash
# Zero OTel dependencies
pip install forge_base
```

#### Installation with OTel
```bash
# OTel SDK only
pip install forge_base[otel]

# OTel + common exporters
pip install forge_base[otel-exporters]

# OTel + auto-instrumentation
pip install forge_base[otel-auto]

# Everything
pip install forge_base[all]
```

#### pyproject.toml
```toml
[project.optional-dependencies]
# OpenTelemetry support (optional)
otel = [
    "opentelemetry-api>=1.20.0",
    "opentelemetry-sdk>=1.20.0",
]

# Common exporters
otel-exporters = [
    "forge_base[otel]",
    "opentelemetry-exporter-jaeger>=1.20.0",
    "opentelemetry-exporter-prometheus>=0.41b0",
    "opentelemetry-exporter-otlp>=1.20.0",
]

# Auto-instrumentation for popular libraries
otel-auto = [
    "forge_base[otel]",
    "opentelemetry-instrumentation-requests>=0.41b0",
    "opentelemetry-instrumentation-flask>=0.41b0",
    "opentelemetry-instrumentation-sqlalchemy>=0.41b0",
    "opentelemetry-instrumentation-redis>=0.41b0",
]

# All optional features
all = [
    "forge_base[dev,sql,otel,otel-exporters,otel-auto]",
]
```

## Consequences

### Positive

✅ **Enterprise-Ready Integration**
- Connects with existing observability infrastructure
- Supports Jaeger, Zipkin, Prometheus, Grafana, commercial APMs
- OTLP protocol for interoperability

✅ **Zero-Code Auto-Instrumentation**
```python
# Before: manual instrumentation
span = tracer.start_span("http_request")
response = requests.get(url)
span.end()

# After (with OTel auto-instrument): automatic!
response = requests.get(url)  # Span created automatically
```

✅ **Automatic Correlation**
```json
{
  "timestamp": "2025-11-05T10:30:00Z",
  "message": "User created",
  "trace_id": "abc123",        // ← Automatic correlation
  "span_id": "def456",
  "service.name": "forge_base-api",
  "usecase.name": "CreateUser"
}
```

✅ **Semantic Conventions**
- Consistent naming following OTel standards
- Standardized attributes recognized by tools
- Better analysis and queries

✅ **Battle-Tested Exporters**
- Maintained by the CNCF community
- Optimized (batching, compression, retry)
- Production-ready

✅ **Rich Ecosystem**
- Instrumentation for 100+ libraries
- Integration with commercial APMs
- Analysis and visualization tools

✅ **Maintains Original Philosophy**
- Zero mandatory deps ✅
- Lightweight by default ✅
- Opt-in, not mandatory ✅
- Cognitive system preserved ✅

### Negative

⚠️ **Heavy Dependencies (when activated)**
```bash
# OTel SDK + exporters + instrumentations
~15-20 additional packages
~50MB of dependencies
```
**Mitigation:** Optional, not installed by default

⚠️ **Setup Complexity**
```python
# OTel setup is not trivial
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter

provider = TracerProvider()
processor = BatchSpanProcessor(JaegerExporter(...))
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)
```
**Mitigation:** ForgeBase abstracts setup via YAML configuration

⚠️ **Performance Overhead**
- ~1-5ms per span
- Memory for buffering
- CPU for serialization

**Mitigation:**
- Configurable sampling (e.g., 10% of requests)
- Batch processing
- Async exporters

⚠️ **Learning Curve**
- Concepts: Providers, Exporters, Processors, Context, Baggage
- Exporter configuration
- Debugging OTel issues

**Mitigation:**
- Clear documentation
- Practical examples
- Sensible defaults

⚠️ **Adapter Maintenance**
- Need to keep up with OTel API updates
- Map ForgeBase ↔ OTel concepts
- Compatibility tests

**Mitigation:**
- Automated tests
- CI/CD for compatibility verification
- Semantic versioning

### Neutral

**Backend Choice**
- User decides: Jaeger, Prometheus, DataDog, etc.
- ForgeBase does not have an opinion on backend
- Configuration via YAML file

**Implementation Coexistence**
- Builtin and OTel coexist
- Choice per environment (dev vs prod)
- Gradual transition possible

## Alternatives Considered

### 1. Mandatory OTel (Rejected)

**Approach:** Make OTel a mandatory dependency.

```toml
dependencies = [
    "pyyaml>=6.0",
    "opentelemetry-api>=1.20.0",  # ← Mandatory
    "opentelemetry-sdk>=1.20.0",
]
```

**Rejected because:**
- Breaks the "lightweight by default" philosophy
- Forces simple users to load 50MB+ deps
- Against the "zero mandatory deps" principle
- Overkill for local/dev/test usage
- Vendor lock-in (even if open source)

### 2. Replace Builtin Implementations (Rejected)

**Approach:** Remove InMemoryTracer, StdoutLogger; use only OTel.

**Rejected because:**
- Loses simplicity for basic use cases
- Tests become slower (OTel setup)
- Dev experience degrades (need to run Jaeger locally)
- Against the autonomy principle

### 3. Fork OTel (Rejected)

**Approach:** Create a custom OTel fork for ForgeBase.

**Rejected because:**
- Heavy maintenance
- Loses community updates
- Fragments the ecosystem
- Reinventing the wheel

### 4. OTLP Protocol Only (Considered, but insufficient)

**Approach:** Support only export via OTLP protocol, without OTel SDK.

```python
# Export spans in OTLP format without SDK
def export_otlp(spans: List[Span]):
    payload = serialize_to_otlp(spans)
    requests.post("http://collector:4318/v1/traces", json=payload)
```

**Partially rejected because:**
- ✅ Lightweight (zero OTel deps)
- Does not have auto-instrumentation
- Does not have automatic context propagation
- Does not have semantic convention helpers
- Does not have instrumentation ecosystem

**Decision:** Use this approach for builtin implementations (direct OTLP export), but also offer full OTel as an option.

### 5. Hybrid Approach (Accepted)

**Our decision:**
- ✅ Builtin implementations (lightweight, default)
- ✅ OTel adapter (optional, enterprise)
- ✅ Direct OTLP export (builtin, no deps)
- ✅ Declarative configuration
- ✅ Preserves unique cognitive system

**Best of both worlds:**
- Simple when you don't need it
- Powerful when you do
- Gradual transition possible

## Implementation Notes

### Phase 1: Foundation (Days 1-2)

```bash
# Create OTel module structure
src/forge_base/observability/otel/
├── __init__.py
├── otel_tracer.py      # Implements TracerPort
├── otel_logger.py      # Implements LoggerPort
├── otel_metrics.py     # Implements TrackMetrics
├── providers.py        # Provider setup
└── auto_instrument.py  # Auto-instrumentation
```

**Acceptance criteria:**
- [ ] OtelTracer fully implements TracerPort
- [ ] Lazy import (works without OTel installed)
- [ ] Docstrings explaining usage
- [ ] Tests with OTel mock

### Phase 2: Configuration (Day 3)

```yaml
# Add to config schema
observability:
  tracing:
    provider: opentelemetry | inmemory | noop
    config:
      service_name: str
      exporter: jaeger | zipkin | otlp
      endpoint: str
      sampling_rate: float
```

**Acceptance criteria:**
- [ ] ConfigLoader validates OTel schema
- [ ] Bootstrap creates OtelTracer if configured
- [ ] Fallback to InMemory if OTel is not installed
- [ ] Clear error if config is incomplete

### Phase 3: Auto-Instrumentation (Days 4-5)

```python
# Implement auto-instrumentation
auto_instrument({
    "requests": True,
    "flask": True,
    "sqlalchemy": True
})
```

**Acceptance criteria:**
- [ ] Support for 5+ popular libraries
- [ ] Documentation of supported libraries
- [ ] Tests with active instrumentation
- [ ] Performance benchmarks

### Phase 4: Cognitive System Integration (Day 6)

```python
# FeedbackManager integrates with OTel
feedback = FeedbackManager(tracer=OtelTracer())
```

**Acceptance criteria:**
- [ ] FeedbackManager works with OtelTracer
- [ ] IntentTracker works with OtelTracer
- [ ] Cognitive spans appear in Jaeger
- [ ] Custom attributes preserved

### Phase 5: Examples and Docs (Day 7)

```markdown
# docs/otel-integration.md
- When to use OTel vs builtin
- How to configure exporters
- How to enable auto-instrumentation
- Performance considerations
- Troubleshooting common issues
```

**Acceptance criteria:**
- [ ] Complete end-to-end example
- [ ] Clear documentation
- [ ] Screenshots of Jaeger/Prometheus
- [ ] Troubleshooting guide

### Phase 6: Testing (Day 8)

```python
# tests/integration/test_otel_integration.py
def test_otel_tracer_compatibility():
    """Verify OtelTracer implements TracerPort."""

def test_auto_instrumentation():
    """Verify auto-instrumentation creates spans."""

def test_exporter_integration():
    """Verify export to Jaeger works."""
```

**Acceptance criteria:**
- [ ] TracerPort compatibility tests
- [ ] Auto-instrumentation tests
- [ ] Exporter tests (mock)
- [ ] Coverage ≥80%

### Estimated Timeline

| Phase | Days | Complexity |
|-------|------|------------|
| 1. Foundation | 2 | High |
| 2. Configuration | 1 | Medium |
| 3. Auto-Instrumentation | 2 | High |
| 4. Cognitive Integration | 1 | Medium |
| 5. Examples and Docs | 1 | Low |
| 6. Testing | 1 | Medium |
| **Total** | **8 days** | - |

### Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| OTel API breaking changes | High | Low | Pin versions, CI tests |
| High performance overhead | Medium | Medium | Benchmarks, sampling |
| Complexity scares users | Medium | High | Clear docs, sensible defaults |
| Adapter maintenance | Medium | Medium | Tests, semantic versioning |
| Instrumentation bugs | Low | Medium | Community maintains, report upstream |

## References

### OpenTelemetry

- **OpenTelemetry Website:** https://opentelemetry.io/
- **OTel Python SDK:** https://github.com/open-telemetry/opentelemetry-python
- **Semantic Conventions:** https://opentelemetry.io/docs/concepts/semantic-conventions/
- **W3C Trace Context:** https://www.w3.org/TR/trace-context/

### Distributed Tracing

- **Distributed Tracing in Practice** by Austin Parker et al.
- **Jaeger Documentation:** https://www.jaegertracing.io/docs/
- **Zipkin Documentation:** https://zipkin.io/

### ForgeBase Related

- **ADR-003: Observability First** — Native observability philosophy
- **TracerPort Implementation** — `src/forge_base/observability/tracer_port.py`
- **FeedbackManager** — Unique cognitive system

## Related ADRs

- [ADR-003: Observability First](003-observability-first.md) — Philosophical foundation
- [ADR-001: Clean Architecture Choice](001-clean-architecture-choice.md) — Boundaries
- [ADR-002: Hexagonal Ports-Adapters](002-hexagonal-ports-adapters.md) — Adapter pattern
- [ADR-005: Dependency Injection](005-dependency-injection.md) — DI container
- [ADR-006: ForgeProcess Integration](006-forgeprocess-integration.md) — Cognitive system

---

**Author:** ForgeBase Development Team
**Date:** 2025-11-05
**Version:** 1.0
**Status:** Accepted for implementation

---

## Appendix A: Comparison Matrix

| Feature | Builtin (InMemory) | OTel Integration |
|---------|-------------------|------------------|
| **Dependencies** | Zero | ~15 packages |
| **Setup Complexity** | Trivial | Medium |
| **Auto-Instrumentation** | Manual | ✅ Automatic |
| **Exporters** | JSON, Memory | 20+ backends |
| **Context Propagation** | Basic | W3C standard |
| **Semantic Conventions** | Custom | OTel standard |
| **Performance Overhead** | ~0.1ms | ~1-5ms |
| **Production Ready** | ✅ Simple cases | ✅ Enterprise |
| **Ecosystem** | ForgeBase only | CNCF ecosystem |
| **Learning Curve** | Low | Medium |
| **Use Case** | Dev, tests, simple prod | Complex prod, microservices |

## Appendix B: Example Configurations

### Local Development
```yaml
observability:
  tracing:
    provider: inmemory  # Lightweight, fast
  logging:
    provider: stdout    # Console output
  metrics:
    provider: builtin   # In-memory
```

### Staging with Jaeger
```yaml
observability:
  tracing:
    provider: opentelemetry
    config:
      service_name: forge_base-staging
      exporter: jaeger
      endpoint: http://jaeger:14268/api/traces
      sampling_rate: 0.5  # 50%

  auto_instrument:
    - requests
    - sqlalchemy
```

### Production with Full Stack
```yaml
observability:
  tracing:
    provider: opentelemetry
    config:
      service_name: forge_base-prod
      exporter: otlp
      endpoint: http://otel-collector:4317
      sampling_rate: 0.1  # 10% (high traffic)

  logging:
    provider: opentelemetry
    config:
      exporter: otlp
      endpoint: http://otel-collector:4317

  metrics:
    provider: opentelemetry
    config:
      exporter: prometheus
      endpoint: http://prometheus:9090
      interval: 60

  auto_instrument:
    - requests
    - flask
    - sqlalchemy
    - redis
    - celery
```

## Appendix C: Migration Path

### For Current ForgeBase Users

**Step 1: Continue using builtin (nothing changes)**
```bash
# Your code continues working
pip install forge_base==0.1.4
```

**Step 2: Try OTel locally**
```bash
pip install forge_base[otel]
# Update config.yaml to use OTel
# Run Jaeger locally: docker run -p 16686:16686 jaegertracing/all-in-one
```

**Step 3: Gradual staging deployment**
```yaml
# Staging: 10% of traces via OTel, rest builtin
observability:
  tracing:
    provider: opentelemetry
    config:
      sampling_rate: 0.1
```

**Step 4: Production rollout**
```yaml
# Production: full OTel
observability:
  tracing:
    provider: opentelemetry
```

**Rollback is trivial:** Change `provider: opentelemetry` → `provider: inmemory` in the config.

---

*"Observability is not an additional layer, but an intrinsic property of cognitive code."*

**— Jorge, The Forge**
