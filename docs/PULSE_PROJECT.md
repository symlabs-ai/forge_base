# ForgePulse — Project Plan

Central implementation document for ForgePulse: optional instrumentation layer
per ValueTrack with CL/CE governance.

**Origin:** [ForgePulse_PROPOSAL.md](ForgePulse_PROPOSAL.md)
**Related ADRs:** [003-observability-first](adr/003-observability-first.md), [007-opentelemetry-integration](adr/007-opentelemetry-integration.md)
**Base version:** ForgeBase 0.2.0
**Status:** In planning

---

## Table of Contents

1. [Vision and Principles](#1-vision-and-principles)
2. [CL/CE Architecture](#2-clce-architecture)
3. [Key Technical Decisions](#3-key-technical-decisions)
4. [Phase Map](#4-phase-map)
5. [Phase 0 — Foundation (no-op)](#5-phase-0--foundation-no-op)
6. [Phase 1 — BASIC/STANDARD + Legacy Heuristic](#6-phase-1--basicstandard--legacy-heuristic)
7. [Phase 2 — Mapping via Spec (CE)](#7-phase-2--mapping-via-spec-ce)
8. [Phase 3 — Optional Decorators + Tracing](#8-phase-3--optional-decorators--tracing)
9. [Phase 4 — Advanced Governance](#9-phase-4--advanced-governance)
10. [Phase 5 — Strict Mode + Reports](#10-phase-5--strict-mode--reports)
11. [Existing Code Reused](#11-existing-code-reused)
12. [Testing Strategy](#12-testing-strategy)
13. [Risks and Mitigations](#13-risks-and-mitigations)
14. [Glossary](#14-glossary)

---

## 1. Vision and Principles

### Problem

ForgeBase measures "technical health" (logs, metrics, traces), but does not measure "value delivered per axis".
Without this connection, the roadmap becomes narrative and each product instruments in its own way.

### Objective

Add to ForgeBase an optional layer (`pulse/`) that instruments executions per ValueTrack
without breaking compatibility, preserving Clean Architecture and enabling CL/CE governance.

### Inviolable Principles

| # | Principle | Verification |
|---|-----------|--------------|
| P1 | **Full compatibility** — ForgeBase without ForgePulse remains identical | All 248+ tests pass without changes |
| P2 | **Opt-in** — Nothing mandatory. Decorators are optional metadata | UseCase does not import anything from `pulse/` |
| P3 | **Clean Architecture intact** — UseCases do not depend on infra | import-linter validates boundaries |
| P4 | **Controlled overhead** — OFF = real zero cost | Benchmark: < 100ns overhead in OFF |
| P5 | **Stable schema** — Events/metrics follow versioning | Versioned dataclass with `schema_version` field |

---

## 2. CL/CE Architecture

### CL — Core Logic (stable core, lives in `forge_base`)

Remains reliable, consistent, and compatible:

- Execution runtime (engine)
- Contracts (interfaces/types) and base schema
- Context propagation (`ExecutionContext`)
- Plugin/hook mechanisms and governance
- Observability protocols (`LoggerProtocol`, `MetricsProtocol`)

**CL does not contain:** customer rules, specific policies, specific exporters.

### CE — Customer Extensions (configurable extensions, live in the product)

Varies by project/tenant/product/environment:

- ValueTrack/SubTrack mappings to UseCases (via YAML spec)
- Monitoring policies (level, sampling, budgets)
- Exporters/sinks (OTEL/Prometheus/ClickHouse/file)
- Custom reports
- Risk classifications and tags

**CE cannot break through CL. CE plugs in via contract (protocols).**

### Where Instrumentation Happens

```
Adapter (HTTP/CLI)
    |
    v
UseCaseRunner (composition root)  <-- creates ExecutionContext, measures start/end/error
    |
    v
UseCaseBase.execute()             <-- remains PURE, no dependency on pulse
    |
    v
Port/Repository                   <-- adapters measure cost/latency/retry via protocols
```

---

## 3. Key Technical Decisions

### TD-1: Context propagation via `contextvars`

**Problem:** Injecting `ExecutionContext` into `execute(input_dto)` violates Clean Architecture.
Thread-local (`threading.local`) does not work with async.

**Decision:** Use `contextvars.ContextVar` (stdlib, async-safe).

```python
# pulse/context.py
from contextvars import ContextVar
_current_context: ContextVar[ExecutionContext | None] = ContextVar('pulse_ctx', default=None)
```

The `UseCaseRunner` sets the context before calling `execute()`.
Any layer can read it without explicit dependency. The `execute()` signature does not change.

**Reference:** `LogContext` in `log_service.py:67-107` already uses a similar pattern with `threading.local`.

### TD-2: Separate metrics protocol (without breaking MetricsProtocol)

**Problem:** The current `MetricsProtocol` (`composition/protocols.py:51-73`) only has `increment()` and `timing()`.
ForgePulse needs `histogram()` and `gauge()`. Extending the existing protocol would break mypy/pyright
for any class implementing `MetricsProtocol` without the new methods.

**Decision:** Keep `MetricsProtocol` intact. ForgePulse defines its own `PulseMetricsProtocol`.

```python
# pulse/protocols.py
class PulseMetricsProtocol(Protocol):
    """Extended protocol for pulse. Does not alter existing MetricsProtocol."""
    def increment(self, name: str, value: int = 1, **tags: Any) -> None: ...
    def timing(self, name: str, value: float, **tags: Any) -> None: ...
    def histogram(self, name: str, value: float, **tags: Any) -> None: ...
    def gauge(self, name: str, value: float, **tags: Any) -> None: ...
```

`TrackMetrics` already implements all 4 methods — satisfies `PulseMetricsProtocol` without changes.
The original `MetricsProtocol` remains with `increment()` and `timing()` — zero breaking change.

**Result:** typing in the ecosystem does not fail when upgrading to 0.3.0.

### TD-3: Monitoring levels as enum with fast-path

**Decision:** `MonitoringLevel` enum with level check before any allocation.

```python
class MonitoringLevel(IntEnum):
    OFF = 0
    BASIC = 1
    STANDARD = 2
    DETAILED = 3
    DIAGNOSTIC = 4
```

Using `IntEnum`, the check `if level >= MonitoringLevel.STANDARD` is an integer comparison (~1ns).
In OFF, the `UseCaseRunner` does a direct passthrough — no `ExecutionContext` created,
no `ContextVar` set, no dict allocated. See TD-3b.

### TD-3b: Real fast-path in OFF (no allocation)

**Problem:** Creating `ExecutionContext` (frozen dataclass) + `ContextVar.set()` costs ~200-500ns.
The "OFF < 100ns" target is unattainable if any object is created.

**Decision:** In OFF, `UseCaseRunner.run()` is a direct passthrough:

```python
def run(self, input_dto: TInput, **ctx_overrides: Any) -> TOutput:
    if self._level == MonitoringLevel.OFF:
        return self._use_case.execute(input_dto)  # zero overhead
    # ... context, measurement, collection (only level > OFF)
```

- OFF: does not create ExecutionContext, does not set ContextVar, does not measure time
- BASIC+: creates full context, sets ContextVar, measures time

**Criterion:** benchmark with real runner (not isolated microbenchmark).

Benchmarks are run on a reference machine and validated by relative comparison
(`runner.run()` vs `use_case.execute()` directly), to avoid nanosecond fluctuations
across environments.

### TD-4: ECM deferred to Phase 4

**Decision:** Extension Compatibility Matrix only makes sense when real CE extensions
exist as separate published packages. Until then, rely on normal semantic versioning.

### TD-5: Reports are structured data, not documents

**Decision:** ForgePulse CL exposes dataclasses with raw data (`PulseReport`).
Formatting into Markdown/JSON is the responsibility of CE or the consuming product.

### TD-6: Standard field name schema (CL contract, CE implementation)

**Problem:** Without a naming contract, each CE invents names for the same metrics
("llm_tokens", "tokensIn", "prompt_tokens") and cross-product comparability dies.

**Decision:** CL defines `PulseFieldNames` — standardized constants for common fields
(LLM, HTTP, DB, etc.). CL **does not measure anything** — it only defines the accepted envelope/shape.
CE implements wrappers/exporters that populate these fields (or not).

```python
# pulse/field_names.py
class PulseFieldNames:
    """Standard names for metric/event fields. CL defines shape, CE populates."""

    # LLM (optional — LLM CE uses it; others ignore)
    LLM_TOKENS_IN = "llm.tokens_in"
    LLM_TOKENS_OUT = "llm.tokens_out"
    LLM_LATENCY_MS = "llm.latency_ms"
    LLM_MODEL = "llm.model"
    LLM_COST = "llm.cost"
    LLM_FALLBACK_TRIGGERED = "llm.fallback_triggered"

    # HTTP (optional)
    HTTP_METHOD = "http.method"
    HTTP_STATUS_CODE = "http.status_code"
    HTTP_LATENCY_MS = "http.latency_ms"

    # DB (optional)
    DB_OPERATION = "db.operation"
    DB_LATENCY_MS = "db.latency_ms"
    DB_ROWS_AFFECTED = "db.rows_affected"
```

This is classic CL/CE: contract in CL, implementation in CE. No dependency on
OpenAI/Claude/etc. client in the core.

**Delivery:** documented and published in 0.3.0 as contract v0.1. Implementation of
specific collectors belongs in CE.

**Tag discipline:** `correlation_id` is never a metric label; user data
does not enter as a tag. High-cardinality identifiers are restricted to tracing
(DETAILED).

### TD-7: Baseline redaction from day 1

**Problem:** `ExecutionContext.extra: dict[str, Any]` and `ctx_overrides` accept arbitrary
data. Without a minimal policy, sensitive keys (`password`, `token`, `secret`,
`authorization`, `api_key`) could leak to exporters/logs from the very first collection.

**Decision:** Phase 0 includes a minimal `RedactionPolicy` applied during
`ExecutionContext` creation (when `level > OFF`):

```python
# pulse/redaction.py
SENSITIVE_PATTERNS: frozenset[str] = frozenset({
    "password", "passwd", "token", "secret",
    "authorization", "api_key", "apikey",
    "credential", "private_key",
})

def redact_keys(data: dict[str, Any], mask: str = "***") -> dict[str, Any]:
    """Masks values of sensitive keys. Applied before any export."""
    return {
        k: mask if _is_sensitive(k) else v
        for k, v in data.items()
    }
```

- Minimal denylist in frozenset (O(1) lookup cost)
- Applied at the collection point, before the exporter receives data
- DIAGNOSTIC **does not include raw payload** by default — requires explicit allowlist
- CE can extend with additional allowlist/denylist via policy

**Result:** door closed from day 1. Cost: ~20 lines of code.

Exporters receive already-redacted data by default. Redaction is applied in the context
(during `ExecutionContext` creation) and again in the export path.

### TD-8: `mapping_source` field in ExecutionContext

**Problem:** Heuristic is useful but creates an illusion of precision. Without knowing the mapping
origin, reports cannot distinguish "declared value" from "inferred value".

**Decision:** `ExecutionContext` includes the `mapping_source` field from Phase 0:

```python
mapping_source: Literal["spec", "decorator", "heuristic", "legacy"] = "legacy"
```

- Phase 0: always `"legacy"` (everything is no-op)
- Phase 1: `"heuristic"` (inference by class/module)
- Phase 2: `"spec"` (YAML mapping)
- Phase 3: `"decorator"` (explicit metadata)

Reports can filter/aggregate by source starting from Phase 1.

---

## 4. Phase Map

ForgePulse is a feature of the 0.3.x series. Each phase is an incremental patch
within the same minor version, ensuring compatibility between patches.

```
Phase 0 --> Phase 1 --> Phase 2 --> Phase 3 --> Phase 4 --> Phase 5
 v0.3.0     v0.3.1     v0.3.2     v0.3.3     v0.3.4     v0.3.5

 Foundation  BASIC/     Spec CE    Decorators  Advanced    Strict +
 (no-op)     STANDARD              + Tracing   Governance  Reports
```

| Phase | Version | Main Deliverable | Prerequisite |
|-------|---------|------------------|--------------|
| 0 | 0.3.0 | ExecutionContext + MonitoringLevel + NoOpCollector | ForgeBase 0.2.0 |
| 1 | 0.3.1 | BASIC/STANDARD collection + legacy heuristic | Phase 0 |
| 2 | 0.3.2 | ValueTrack mapping via YAML spec | Phase 1 |
| 3 | 0.3.3 | Opt-in decorators + tracing per span | Phase 2 |
| 4 | 0.3.4 | Sampling, budgets, ECM | Phase 3 |
| 5 | 0.3.5 | Strict mode + structured PulseReport | Phase 4 |

**Versioning rule:** 0.3.x patches are additive — each patch adds
functionality without breaking what the previous one delivered. A product depending on
`forge_base>=0.3.0,<0.4.0` receives all phases without breaking changes.

---

## 5. Phase 0 — Foundation (no-op)

**Patch:** 0.3.0
**Objective:** Base infrastructure with zero cost when disabled.

### File Structure

```
src/forge_base/pulse/
    __init__.py              # public re-exports
    context.py               # ExecutionContext + ContextVar
    level.py                 # MonitoringLevel enum
    collector.py             # PulseCollector (interface) + NoOpCollector
    runner.py                # UseCaseRunner (wraps execute with context)
    protocols.py             # PulseMetricsProtocol + PulseExporterProtocol (contracts)
    field_names.py           # PulseFieldNames — naming contract (CL)
    redaction.py             # RedactionPolicy — minimal sensitive key denylist
    _version.py              # PULSE_SCHEMA_VERSION = "0.1"
```

### Deliverables

#### 5.1 — ExecutionContext (`context.py`)

```python
@dataclass(frozen=True)
class ExecutionContext:
    correlation_id: str
    tenant_id: str = "default"
    value_track: str = "legacy"
    subtrack: str = "legacy"
    feature: str = ""
    use_case: str = ""
    mapping_source: Literal["spec", "decorator", "heuristic", "legacy"] = "legacy"
    version: str = ""
    environment: str = "development"
    level: MonitoringLevel = MonitoringLevel.OFF
    extra: dict[str, Any] = field(default_factory=dict)

# Async-safe propagation
_current_context: ContextVar[ExecutionContext | None] = ContextVar('pulse_ctx', default=None)

def get_context() -> ExecutionContext | None: ...
def set_context(ctx: ExecutionContext) -> Token: ...
```

- `frozen=True` for immutability (safe in async/threads)
- `ContextVar` from stdlib (works with asyncio, threads, and taskgroups)
- `extra: dict[str, Any]` — accepts numeric values without stringifying
- `mapping_source` — tracks mapping origin (spec/decorator/heuristic/legacy)
- Fields with defaults = legacy works without configuring anything
- `extra` passes through `redact_keys()` during creation (when level > OFF)
- `extra` accepts only JSON-like types (`str`, `int`, `float`, `bool`, `None`, `list`, `dict`);
  non-serializable values are discarded/normalized with a counter of discarded events

#### 5.2 — MonitoringLevel (`level.py`)

```python
class MonitoringLevel(IntEnum):
    OFF = 0           # real no-op, cost ~0
    BASIC = 1         # duration + count + success/error
    STANDARD = 2      # + latency per adapter + errors per stage
    DETAILED = 3      # + tracing + cost (tokens/cpu)
    DIAGNOSTIC = 4    # + profiling/payload (only by flag)
```

#### 5.3 — PulseCollector + NoOpCollector (`collector.py`)

```python
class PulseCollector(Protocol):
    def on_start(self, ctx: ExecutionContext) -> None: ...
    def on_success(self, ctx: ExecutionContext, duration_ms: float) -> None: ...
    def on_error(self, ctx: ExecutionContext, error: Exception, duration_ms: float) -> None: ...

class NoOpCollector:
    """Zero cost. Used when level=OFF."""
    def on_start(self, ctx: ExecutionContext) -> None: pass
    def on_success(self, ctx: ExecutionContext, duration_ms: float) -> None: pass
    def on_error(self, ctx: ExecutionContext, error: Exception, duration_ms: float) -> None: pass
```

#### 5.4 — UseCaseRunner (`runner.py`)

```python
class UseCaseRunner(Generic[TInput, TOutput]):
    """Wraps execute() with context + collection. Lives in the composition root."""

    def __init__(
        self,
        use_case: UseCaseBase[TInput, TOutput],
        collector: PulseCollector | None = None,
        level: MonitoringLevel = MonitoringLevel.OFF,
    ): ...

    def run(self, input_dto: TInput, **ctx_overrides: Any) -> TOutput:
        # FAST-PATH: OFF = direct passthrough, zero allocation
        if self._level == MonitoringLevel.OFF:
            return self._use_case.execute(input_dto)

        # INSTRUMENTED PATH (level > OFF):
        # 1. Creates ExecutionContext (with use_case inference from class name)
        # 2. Applies redact_keys() to extra/ctx_overrides
        # 3. Sets ContextVar
        # 4. Calls collector.on_start()
        # 5. Calls use_case.execute(input_dto)
        # 6. Calls collector.on_success() or on_error()
        # 7. Restores ContextVar
        # 8. Returns result
        ...
```

#### 5.5 — Protocols (`protocols.py`)

```python
class PulseMetricsProtocol(Protocol):
    """Extended protocol for pulse. Original MetricsProtocol does not change."""
    def increment(self, name: str, value: int = 1, **tags: Any) -> None: ...
    def timing(self, name: str, value: float, **tags: Any) -> None: ...
    def histogram(self, name: str, value: float, **tags: Any) -> None: ...
    def gauge(self, name: str, value: float, **tags: Any) -> None: ...

class PulseExporterProtocol(Protocol):
    """CE contract: anyone wanting to export data implements this."""
    def export_execution(self, ctx: ExecutionContext, duration_ms: float, success: bool) -> None: ...
```

`TrackMetrics` already satisfies `PulseMetricsProtocol` without any changes.
`MetricsProtocol` in `composition/protocols.py` remains intact.

#### 5.6 — PulseFieldNames (`field_names.py`)

Standard naming constants for metric/event fields.
Contract v0.1 — CL defines shape, CE populates. See TD-6.

#### 5.7 — RedactionPolicy (`redaction.py`)

Minimal sensitive key denylist applied during context creation.
Keys such as `password`, `token`, `secret`, `authorization`, `api_key` are masked.
See TD-7.

### Acceptance Criteria — Phase 0

**Compatibility and boundaries:**
- [ ] All 248+ existing tests pass without changes
- [ ] `UseCaseBase.execute()` unchanged (signature and behavior)
- [ ] `MetricsProtocol` in `composition/protocols.py` unchanged (zero breaking change in typing)
- [ ] import-linter updated for `forge_base` (fix root_package) and with rules for `pulse/`:
  - `application/*` does not import `pulse/*`
  - `domain/*` does not import `pulse/*`
  - `pulse/*` does not import `adapters/*` or `infrastructure/*`
- [ ] `pulse/` is not imported by any existing module (zero coupling)
- [ ] Pipeline fails if boundary is violated

**Functionality:**
- [ ] `import forge_base.pulse` works
- [ ] `ExecutionContext` with `extra: dict[str, Any]` (accepts numeric values)
- [ ] `ExecutionContext.mapping_source` present with default `"legacy"`
- [ ] `ExecutionContext` propagated via `contextvars` and readable from any layer
- [ ] `PulseMetricsProtocol` defined in `pulse/protocols.py` (does not alter existing MetricsProtocol)
- [ ] `PulseFieldNames` published as contract v0.1 (LLM/HTTP/DB names)
- [ ] `redact_keys()` masks sensitive keys (`password`, `token`, `secret`, `authorization`, `api_key`)

**Performance:**
- [ ] `UseCaseRunner` with `level=OFF` does direct passthrough (does not create ExecutionContext)
- [ ] Real benchmark with runner: OFF < 100ns overhead

**Documentation:**
- [ ] ADR-008 written documenting CL/CE decision and ForgePulse

### New Tests

```
tests/unit/pulse/
    test_context.py          # ExecutionContext creation, frozen, defaults, ContextVar, mapping_source
    test_level.py            # MonitoringLevel comparisons, IntEnum behavior
    test_collector.py        # NoOpCollector does nothing, protocol check
    test_runner.py           # UseCaseRunner OFF=passthrough, with mock collector, propagated context
    test_protocols.py        # PulseMetricsProtocol satisfied by TrackMetrics
    test_field_names.py      # PulseFieldNames constants exist and are strings
    test_redaction.py        # Sensitive keys masked, normal keys preserved
tests/benchmarks/
    bench_pulse_overhead.py  # OFF < 100ns (with real runner), BASIC < 10us
```

---

## 6. Phase 1 — BASIC/STANDARD + Legacy Heuristic

**Patch:** 0.3.1
**Prerequisite:** Phase 0 complete
**Objective:** First real metric collection per use case, with automatic legacy fallback.

### File Structure (new)

```
src/forge_base/pulse/
    basic_collector.py       # BASIC/STANDARD implementation
    heuristic.py             # Automatic value_track/feature inference
    report.py                # PulseSnapshot dataclass (raw data)
```

### Deliverables

#### 6.1 — BasicCollector (`basic_collector.py`)

Implements `PulseCollector` using the existing `TrackMetrics`.

**BASIC level collects:**
- `pulse.execution.count` (counter, per use_case + value_track)
- `pulse.execution.duration_ms` (histogram, per use_case + value_track)
- `pulse.execution.errors` (counter, per use_case + value_track + error_type)
- `pulse.execution.success` (counter, per use_case + value_track)

**STANDARD level adds:**
- Metrics with `subtrack` label
- `pulse.adapter.duration_ms` (histogram, per adapter + value_track)
- Error count per stage (before/during/after execute)

#### 6.2 — Legacy Heuristic (`heuristic.py`)

```python
def infer_context(use_case: UseCaseBase) -> dict[str, str]:
    """Infers value_track, subtrack, feature from class/module."""
    cls = type(use_case)
    module = cls.__module__           # e.g.: "my_app.billing.usecases.create_invoice"
    class_name = cls.__name__         # e.g.: "CreateInvoiceUseCase"

    return {
        "use_case": class_name,
        "feature": _extract_feature(module),     # "create_invoice"
        "value_track": "legacy",                  # fallback
        "subtrack": _extract_domain(module),      # "billing"
    }
```

- Uses module name to infer domain/feature
- `value_track` stays `"legacy"` until CE spec provides mapping (Phase 2)
- Zero configuration needed

#### 6.3 — PulseSnapshot (`report.py`)

```python
@dataclass
class PulseSnapshot:
    """Raw data from an observation window. Not a formatted report."""
    timestamp: float
    schema_version: str
    level: MonitoringLevel
    executions: list[ExecutionRecord]
    counters: dict[str, int]
    histograms: dict[str, HistogramStats]
```

### Acceptance Criteria — Phase 1

- [ ] `UseCaseRunner(level=BASIC)` collects duration + count + success/error
- [ ] Heuristic infers `use_case`, `feature`, `subtrack` without configuration
- [ ] `value_track="legacy"` for all use cases without mapping
- [ ] `PulseSnapshot` generated with real data after executions
- [ ] BASIC overhead < 10us per execution (benchmark)
- [ ] Integration with existing `TrackMetrics` (reuses, does not duplicate)
- [ ] No changes to existing code outside `pulse/`

### New Tests

```
tests/unit/pulse/
    test_basic_collector.py  # Correct collection per level
    test_heuristic.py        # Context inference from class/module
    test_report.py           # PulseSnapshot generation and serialization
tests/integration/pulse/
    test_runner_basic.py     # UseCaseRunner with BasicCollector end-to-end
```

---

## 7. Phase 2 — Mapping via Spec (CE)

**Patch:** 0.3.2
**Prerequisite:** Phase 1 complete
**Objective:** Products map use cases to real ValueTracks without touching code.

### File Structure (new)

```
src/forge_base/pulse/
    value_tracks.py          # ValueTrackRegistry + spec loader
    spec_schema.py           # YAML mapping schema
```

### Deliverables

#### 7.1 — ValueTrackRegistry (`value_tracks.py`)

```python
class ValueTrackRegistry:
    """Resolves use_case -> (value_track, subtrack, tags)."""

    def load_from_yaml(self, path: str) -> None: ...
    def load_from_dict(self, data: dict) -> None: ...
    def resolve(self, use_case_name: str) -> ValueTrackMapping | None: ...
```

#### 7.2 — Spec YAML (CE example, does not live in ForgeBase)

```yaml
# forgepulse.value_tracks.yml (in the product, not in the lib)
schema_version: "0.1"

value_tracks:
  cost_governance:
    description: "Cost governance"
    usecases:
      - CreateInvoiceUseCase
      - ProcessPaymentUseCase
    subtracks:
      billing: [CreateInvoiceUseCase]
      payments: [ProcessPaymentUseCase]
    tags:
      domain: financial
      risk: medium

  reliability:
    description: "Service reliability"
    usecases:
      - HealthCheckUseCase
      - RetryOperationUseCase
    tags:
      domain: infrastructure
      risk: high
```

#### 7.3 — Resolution Order in UseCaseRunner

```
1. ValueTrackRegistry (CE spec)      -> explicit mapping
2. Decorator metadata (if present)   -> Phase 3
3. Legacy heuristic (Phase 1)        -> automatic fallback
```

### Acceptance Criteria — Phase 2

- [ ] `ValueTrackRegistry.load_from_yaml()` loads valid spec
- [ ] `ValueTrackRegistry.resolve("CreateInvoiceUseCase")` returns correct mapping
- [ ] `UseCaseRunner` queries registry before heuristic
- [ ] Metrics grouped by real `value_track` (no longer just "legacy")
- [ ] Invalid spec generates `ConfigurationError` (domain error, not crash)
- [ ] Versioned schema (`schema_version` validated)
- [ ] Documentation: CE guide "how to map your ValueTracks"

### New Tests

```
tests/unit/pulse/
    test_value_tracks.py     # Registry load, resolve, fallback
    test_spec_schema.py      # Valid/invalid YAML spec validation
tests/integration/pulse/
    test_runner_with_spec.py # End-to-end with loaded CE spec
```

---

## 8. Phase 3 — Optional Decorators + Tracing

**Patch:** 0.3.3
**Prerequisite:** Phase 2 complete
**Objective:** Precision in new modules via metadata-only decorators and per-span tracing.

### File Structure (new)

```
src/forge_base/pulse/
    decorators.py            # @pulse_track, @pulse_span (metadata only)
    tracing.py               # Integration with existing TracerPort
```

### Deliverables

#### 8.1 — Metadata-only Decorators (`decorators.py`)

```python
def pulse_track(
    value_track: str,
    subtrack: str = "",
    tags: dict[str, str] | None = None,
) -> Callable:
    """Marks a use case with a ValueTrack. Does NOT instrument — only annotates metadata."""
    def decorator(cls):
        cls._pulse_metadata = PulseMetadata(value_track, subtrack, tags or {})
        return cls  # does not wrap, does not alter behavior
    return decorator

# Usage:
@pulse_track(value_track="cost_governance", subtrack="billing")
class CreateInvoiceUseCase(UseCaseBase[CreateInvoiceInput, InvoiceOutput]):
    def execute(self, input_dto): ...
```

- Decorator **does not wrap** the class/method
- Only adds `_pulse_metadata` attribute
- UseCaseRunner reads the attribute during context resolution (priority 2, between spec and heuristic)
- If the developer doesn't use it, nothing changes

#### 8.2 — Integrated Tracing (`tracing.py`)

```python
class PulseTracer:
    """Creates automatic spans linked to ExecutionContext."""

    def __init__(self, tracer: TracerPort, level: MonitoringLevel): ...

    def execution_span(self, ctx: ExecutionContext) -> Span | None:
        """Creates span for use case execution. Returns None if level < DETAILED."""
        if self.level < MonitoringLevel.DETAILED:
            return None
        ...
```

- Reuses existing `TracerPort` and `Span` (`observability/tracer_port.py`)
- Spans linked to `ExecutionContext.correlation_id`
- DETAILED level creates spans; BASIC/STANDARD do not

### Acceptance Criteria — Phase 3

- [ ] `@pulse_track` does not alter class behavior (zero overhead)
- [ ] `UseCaseRunner` resolves decorator metadata (priority 2)
- [ ] Final order: Spec > Decorator > Heuristic
- [ ] DETAILED level creates spans linked to context
- [ ] Spans reuse existing `TracerPort` (does not create parallel system)
- [ ] `NoOpTracer` continues working (DETAILED without tracer = noop)
- [ ] Decorators are optional — no existing module requires them

### New Tests

```
tests/unit/pulse/
    test_decorators.py       # Metadata set, class not altered, priority
    test_tracing.py          # Spans created per level, context linking
tests/integration/pulse/
    test_runner_decorated.py # Runner + decorator + spec + heuristic combined
```

---

## 9. Phase 4 — Advanced Governance

**Patch:** 0.3.4
**Prerequisite:** Phase 3 complete
**Objective:** Fine-grained control of telemetry cost and extension validation.

### File Structure (new)

```
src/forge_base/pulse/
    policy.py                # SamplingPolicy, BudgetPolicy
    ecm.py                   # ExtensionCompatibilityMatrix
    buffer.py                # AsyncBuffer with controlled drop
```

### Deliverables

#### 9.1 — Sampling Policy (`policy.py`)

```python
@dataclass
class SamplingPolicy:
    """Decides whether an execution should be instrumented."""
    default_rate: float = 1.0                    # 100% by default
    by_value_track: dict[str, float] = field(default_factory=dict)
    by_tenant: dict[str, float] = field(default_factory=dict)

    def should_sample(self, ctx: ExecutionContext) -> bool: ...
```

#### 9.2 — Budget Policy (`policy.py`)

```python
@dataclass
class BudgetPolicy:
    """Limits the amount of telemetry per execution."""
    max_spans_per_execution: int = 100
    max_events_per_execution: int = 50
    max_bytes_per_execution: int = 64 * 1024   # 64KB
```

#### 9.3 — ECM (`ecm.py`)

```python
class ExtensionCompatibilityMatrix:
    """Validates whether CE extensions are compatible with the ForgeBase/Pulse version."""

    def register_extension(self, name: str, version: str, requires_pulse: str): ...
    def validate(self, pulse_version: str) -> list[IncompatibleExtension]: ...
    def validate_or_raise(self, pulse_version: str) -> None: ...
```

- Validation on startup via `BuilderBase`
- Incompatible extension: disables (warn) or fails (strict), per policy
- Lightweight structure — no database, no network, no lock

#### 9.4 — AsyncBuffer (`buffer.py`)

```python
class AsyncBuffer:
    """Async buffer for export with controlled drop."""

    def __init__(self, max_size: int = 10_000, drop_policy: str = "oldest"): ...
    def push(self, record: ExecutionRecord) -> bool: ...   # False if dropped
    def flush(self, exporter: PulseExporterProtocol) -> int: ...  # returns N exported
```

### Acceptance Criteria — Phase 4

- [ ] Sampling by value_track and tenant works
- [ ] Budget limits spans/events/bytes per execution
- [ ] ECM validates extensions on startup
- [ ] Incompatible extension generates warning or error per policy
- [ ] AsyncBuffer with controlled drop does not block runtime
- [ ] Policy check overhead < 1us

### New Tests

```
tests/unit/pulse/
    test_policy.py           # Sampling rates, budget limits
    test_ecm.py              # Compatibility, incompatibility, strict mode
    test_buffer.py           # Capacity, drop, flush
tests/property_based/
    test_sampling_properties.py  # Sampling rate converges to expected
```

---

## 10. Phase 5 — Strict Mode + Reports

**Patch:** 0.3.5
**Prerequisite:** Phase 4 complete
**Objective:** Strict mode per scope and structured data for reports.

### File Structure (new)

```
src/forge_base/pulse/
    strict.py                # StrictMode: validates that every use case has a ValueTrack
    report.py                # (extends) PulseReport with aggregations
```

### Deliverables

#### 10.1 — Strict Mode (`strict.py`)

```python
class StrictMode:
    """Validates that all use cases in a scope have a mapped ValueTrack."""

    def __init__(self, scope: str = "*"):  # scope can be module or package
        ...

    def validate(self, registry: ValueTrackRegistry, discovered: list[str]) -> StrictReport:
        """Returns list of use cases without mapping."""
        ...
```

- Activated per scope (e.g., `scope="my_app.billing"`)
- Does not block execution — generates a report
- `StrictReport` exposes `ok: bool` and `missing: list[str]`
- In CI, `assert_ok()` fails the pipeline when `ok=False`
- Useful for CI: fail if new use case without ValueTrack

#### 10.2 — Extended PulseReport (`report.py`)

```python
@dataclass
class PulseReport:
    """Structured data for consumption by CE reports."""
    snapshot: PulseSnapshot
    by_value_track: dict[str, ValueTrackStats]
    by_tenant: dict[str, TenantStats]
    unmapped_usecases: list[str]
    schema_version: str

@dataclass
class ValueTrackStats:
    total_executions: int
    error_rate: float
    p50_duration_ms: float
    p95_duration_ms: float
    p99_duration_ms: float
```

- **Raw data, not a formatted report**
- CE or product converts to Markdown/JSON/dashboard

### Acceptance Criteria — Phase 5

- [ ] StrictMode identifies use cases without mapping
- [ ] PulseReport aggregates by value_track and tenant
- [ ] Data exportable as dict/JSON
- [ ] Integrable with CI (exit code != 0 if strict fails)
- [ ] Complete documentation: adoption guide per phase

---

## 11. Existing Code Reused

Inventory of what already exists and will be reused (not reimplemented):

| Component | File | Use in ForgePulse |
|-----------|------|-------------------|
| `TrackMetrics` | `observability/track_metrics.py` | Metrics backend for BasicCollector |
| `LogService` + `LogContext` | `observability/log_service.py` | Context propagation pattern (reference for TD-1) |
| `TracerPort` + `Span` | `observability/tracer_port.py` | Tracing backend for Phase 3 |
| `NoOpTracer` | `observability/tracer_port.py:325` | Pattern for OFF level |
| `InMemoryTracer` | `observability/tracer_port.py:377` | Tracing in dev/tests |
| `@track_metrics` | `application/decorators/track_metrics.py` | Pattern for opt-in decorators (reference for Phase 3) |
| `BuilderBase` | `composition/builder.py` | Composition root where Runner plugs in |
| `BuildContextBase` | `composition/build_context.py` | Context with cache, env resolution |
| `BuildSpecBase` | `composition/build_spec.py` | Base for ValueTrack YAML spec |
| `PluginRegistryBase` | `composition/plugin_registry.py` | Base for ECM |
| `LoggerProtocol` | `composition/protocols.py` | Logging contract |
| `MetricsProtocol` | `composition/protocols.py` | Metrics contract (remains intact; pulse uses `PulseMetricsProtocol`) |
| `UseCaseBase` | `application/usecase_base.py` | Interface that Runner wraps (does not modify) |
| `DependencyContainer` | `core_init.py` | DI for registering Pulse services |

---

## 12. Testing Strategy

### By Type

| Type | Directory | What It Validates |
|------|-----------|-------------------|
| Unit | `tests/unit/pulse/` | Each component in isolation |
| Integration | `tests/integration/pulse/` | Runner + Collector + Registry end-to-end |
| Property-based | `tests/property_based/` | Sampling convergence, context immutability |
| Benchmark | `tests/benchmarks/` | Overhead per level (OFF < 100ns, BASIC < 10us) |
| Contract | `tests/contract_tests/` | PulseCollector protocol compliance |
| Regression | All 248+ existing | Nothing breaks (P1) |

### Golden Rule

**No existing test may be modified or removed because of ForgePulse.**
If an existing test fails, it's a bug in ForgePulse, not in the test.

### Pytest Markers

```ini
[tool:pytest]
markers =
    pulse: ForgePulse tests
    pulse_benchmark: Overhead benchmarks
```

---

## 13. Risks and Mitigations

| # | Risk | Impact | Mitigation |
|---|------|--------|------------|
| R1 | Scope creep — each phase attracts "just one more feature" | High | Each phase has closed acceptance criteria. Extra features go to the next phase. |
| R2 | Performance — instrumentation degrades runtime | High | Mandatory benchmarks per phase. OFF = proven direct passthrough. |
| R3 | Coupling — pulse contaminates existing layers | High | import-linter validates boundaries. Pipeline fails if violated. |
| R4 | Typing breaks in the ecosystem | Medium | `MetricsProtocol` intact. Pulse uses its own `PulseMetricsProtocol` (TD-2). |
| R5 | Nobody uses ValueTracks in practice | Medium | Legacy heuristic ensures value from Phase 1 without configuration. |
| R6 | Complexity of contextvars with web frameworks | Medium | Test with Flask, FastAPI. ASGI frameworks propagate contextvars natively. |
| R7 | YAML spec grows without governance | Low | Versioned schema + validation in Phase 2. |
| R8 | PII leakage via `extra`/tags | High | `RedactionPolicy` with denylist from Phase 0 (TD-7). DIAGNOSTIC requires explicit allowlist. |

---

## 14. Glossary

| Term | Definition |
|------|------------|
| **ValueTrack** | Measurable value axis (e.g., Cost Governance, Reliability, Security) |
| **SubTrack** | Subdivision of a ValueTrack (e.g., billing, payments within cost_governance) |
| **CL** | Core Logic — stable core of ForgeBase |
| **CE** | Customer Extensions — configurable extensions per product/customer |
| **ECM** | Extension Compatibility Matrix — extension compatibility validation |
| **MonitoringLevel** | Instrumentation level (OFF/BASIC/STANDARD/DETAILED/DIAGNOSTIC) |
| **ExecutionContext** | Immutable context propagated throughout execution via contextvars |
| **PulseCollector** | Interface for metric collection per level |
| **UseCaseRunner** | Wrapper in the composition root that instruments execute() without altering UseCase |
| **PulseSnapshot** | Raw data from an observation window |
| **PulseReport** | Structured aggregation for report consumption |
| **Legacy heuristic** | Automatic context inference from class/module name |
| **Sampling** | Probabilistic sampling for volume control |
| **Budget** | Telemetry limit per execution (spans, events, bytes) |
| **Strict Mode** | Validation that every use case has a mapped ValueTrack |
| **PulseFieldNames** | Standard naming constants for metric fields (CL contract) |
| **PulseMetricsProtocol** | Extended metrics protocol for pulse (does not alter MetricsProtocol) |
| **RedactionPolicy** | Sensitive key denylist applied during data collection |
| **mapping_source** | Field identifying mapping origin (spec/decorator/heuristic/legacy) |

---

## 15. Execution Plan and Evolution Log

### Conventions

- Each phase is a single PR. The PR is only merged when all acceptance criteria are green.
- Evolution log is maintained in this document (section 15.2) upon completing each phase.
- Blockers are recorded with date, description, and resolution.
- Decisions made during implementation that deviate from the plan are noted as "Deviation".

### 15.1 — Execution Checklist

#### Pre-Phase 0: Groundwork

- [ ] Fix `.import-linter`: `root_package = forgebase` -> `root_package = forge_base`
- [ ] Validate that import-linter runs and passes with corrected config
- [ ] Confirm that all 248+ tests pass in the current state (baseline)

#### Phase 0 — Foundation (0.3.0)

| # | Task | File(s) | Status |
|---|------|---------|--------|
| F0.1 | Create `pulse/` package with `__init__.py` | `pulse/__init__.py` | Pending |
| F0.2 | Implement `MonitoringLevel` (IntEnum) | `pulse/level.py` | Pending |
| F0.3 | Implement `ExecutionContext` (frozen dataclass + ContextVar) | `pulse/context.py` | Pending |
| F0.4 | Implement `PulseCollector` (Protocol) + `NoOpCollector` | `pulse/collector.py` | Pending |
| F0.5 | Implement `PulseMetricsProtocol` + `PulseExporterProtocol` | `pulse/protocols.py` | Pending |
| F0.6 | Implement `PulseFieldNames` (constants v0.1) | `pulse/field_names.py` | Pending |
| F0.7 | Implement `redact_keys()` + denylist | `pulse/redaction.py` | Pending |
| F0.8 | Implement `UseCaseRunner` with OFF fast-path | `pulse/runner.py` | Pending |
| F0.9 | Create `_version.py` with `PULSE_SCHEMA_VERSION` | `pulse/_version.py` | Pending |
| F0.10 | Add import-linter rules for `pulse/` | `.import-linter` | Pending |
| F0.11 | Write unit tests (context, level, collector, runner, protocols, redaction) | `tests/unit/pulse/` | Pending |
| F0.12 | Write benchmark OFF vs direct execute | `tests/benchmarks/` | Pending |
| F0.13 | Write ADR-008 (CL/CE + ForgePulse) | `docs/adr/008-forgepulse-clce.md` | Pending |
| F0.14 | Run full suite (248+ old tests + new) | CI | Pending |
| F0.15 | Bump version to 0.3.0, tag, CHANGELOG | `pyproject.toml`, `CHANGELOG.md` | Pending |

#### Phase 1 — BASIC/STANDARD (0.3.1)

| # | Task | File(s) | Status |
|---|------|---------|--------|
| F1.1 | Implement `BasicCollector` (BASIC + STANDARD) | `pulse/basic_collector.py` | Pending |
| F1.2 | Implement `infer_context()` heuristic | `pulse/heuristic.py` | Pending |
| F1.3 | Implement `PulseSnapshot` + `ExecutionRecord` | `pulse/report.py` | Pending |
| F1.4 | Integrate `BasicCollector` with existing `TrackMetrics` | `pulse/basic_collector.py` | Pending |
| F1.5 | Unit tests (basic_collector, heuristic, report) | `tests/unit/pulse/` | Pending |
| F1.6 | Integration test Runner + BasicCollector end-to-end | `tests/integration/pulse/` | Pending |
| F1.7 | Benchmark BASIC < 10us | `tests/benchmarks/` | Pending |
| F1.8 | Bump version to 0.3.1, tag, CHANGELOG | `pyproject.toml`, `CHANGELOG.md` | Pending |

#### Phase 2 — Mapping via Spec (0.3.2)

| # | Task | File(s) | Status |
|---|------|---------|--------|
| F2.1 | Implement `ValueTrackRegistry` (load YAML, resolve) | `pulse/value_tracks.py` | Pending |
| F2.2 | Implement YAML schema validation | `pulse/spec_schema.py` | Pending |
| F2.3 | Integrate registry in `UseCaseRunner` (spec > heuristic) | `pulse/runner.py` | Pending |
| F2.4 | Unit tests (value_tracks, spec_schema) | `tests/unit/pulse/` | Pending |
| F2.5 | Integration test Runner + CE spec | `tests/integration/pulse/` | Pending |
| F2.6 | Documentation: CE guide "how to map your ValueTracks" | `docs/users/` | Pending |
| F2.7 | Bump version to 0.3.2, tag, CHANGELOG | `pyproject.toml`, `CHANGELOG.md` | Pending |

#### Phase 3 — Decorators + Tracing (0.3.3)

| # | Task | File(s) | Status |
|---|------|---------|--------|
| F3.1 | Implement `@pulse_track` (metadata-only) | `pulse/decorators.py` | Pending |
| F3.2 | Implement `PulseTracer` (integration with `TracerPort`) | `pulse/tracing.py` | Pending |
| F3.3 | Integrate decorator in Runner (spec > decorator > heuristic) | `pulse/runner.py` | Pending |
| F3.4 | Implement complete `RedactionPolicy` for DIAGNOSTIC | `pulse/redaction.py` | Pending |
| F3.5 | Unit tests (decorators, tracing) | `tests/unit/pulse/` | Pending |
| F3.6 | Integration test Runner + decorator + spec + heuristic | `tests/integration/pulse/` | Pending |
| F3.7 | Bump version to 0.3.3, tag, CHANGELOG | `pyproject.toml`, `CHANGELOG.md` | Pending |

#### Phase 4 — Advanced Governance (0.3.4)

| # | Task | File(s) | Status |
|---|------|---------|--------|
| F4.1 | Implement `SamplingPolicy` + `BudgetPolicy` | `pulse/policy.py` | Pending |
| F4.2 | Implement `ExtensionCompatibilityMatrix` | `pulse/ecm.py` | Pending |
| F4.3 | Implement `AsyncBuffer` with controlled drop | `pulse/buffer.py` | Pending |
| F4.4 | Unit tests (policy, ecm, buffer) | `tests/unit/pulse/` | Pending |
| F4.5 | Property-based tests (sampling convergence) | `tests/property_based/` | Pending |
| F4.6 | Bump version to 0.3.4, tag, CHANGELOG | `pyproject.toml`, `CHANGELOG.md` | Pending |

#### Phase 5 — Strict Mode + Reports (0.3.5)

| # | Task | File(s) | Status |
|---|------|---------|--------|
| F5.1 | Implement `StrictMode` + `StrictReport` (`ok`, `missing`, `assert_ok()`) | `pulse/strict.py` | Pending |
| F5.2 | Implement `PulseReport` + `ValueTrackStats` with `to_dict()` | `pulse/report.py` | Pending |
| F5.3 | Unit tests (strict, report serialization) | `tests/unit/pulse/` | Pending |
| F5.4 | Integration test CI (strict mode fails pipeline) | `tests/integration/pulse/` | Pending |
| F5.5 | Complete documentation: adoption guide per phase | `docs/users/` | Pending |
| F5.6 | Bump version to 0.3.5, tag, CHANGELOG | `pyproject.toml`, `CHANGELOG.md` | Pending |

---

### 15.2 — Evolution Log

Execution history. Update upon completing each phase.

#### Phase 0

| Date | Event | Notes |
|------|-------|-------|
| — | *Not yet started* | — |

#### Phase 1

| Date | Event | Notes |
|------|-------|-------|
| — | *Not yet started* | — |

#### Phase 2

| Date | Event | Notes |
|------|-------|-------|
| — | *Not yet started* | — |

#### Phase 3

| Date | Event | Notes |
|------|-------|-------|
| — | *Not yet started* | — |

#### Phase 4

| Date | Event | Notes |
|------|-------|-------|
| — | *Not yet started* | — |

#### Phase 5

| Date | Event | Notes |
|------|-------|-------|
| — | *Not yet started* | — |

---

### 15.3 — Blocker Log

| Date | Phase | Description | Resolution | Status |
|------|-------|-------------|------------|--------|
| — | — | *No blockers recorded* | — | — |

---

### 15.4 — Deviation Log

Decisions made during implementation that diverge from the original plan.

| Date | Phase | Deviation | Justification | Impact |
|------|-------|-----------|---------------|--------|
| — | — | *No deviations recorded* | — | — |

---

*Living document. Update upon each completed phase.*
