# ForgePulse -- Cookbook

Complete reference with recipes for each ForgePulse feature.
Each section contains a brief explanation and a runnable snippet.

> Prerequisite: read the [Quick Start](pulse_quick_start.md) first.

---

## Table of Contents

1. [Monitoring Levels](#1-monitoring-levels)
2. [Mapping Hierarchy](#2-mapping-hierarchy)
3. [@pulse_meta](#3-pulse_meta)
4. [ValueTrackRegistry (YAML)](#4-valuetrackregistry-yaml)
5. [Tags](#5-tags)
6. [pulse_span](#6-pulse_span)
7. [BudgetPolicy](#7-budgetpolicy)
8. [SamplingPolicy](#8-samplingpolicy)
9. [ExportPipeline](#9-exportpipeline)
10. [DashboardSummary](#10-dashboardsummary)
11. [ECM](#11-ecm)
12. [Redaction](#12-redaction)
13. [Testing with FakeMetricsCollector](#13-testing-with-fakemetricscollector)
14. [Quick Reference](#14-quick-reference)

---

## 1. Monitoring Levels

`MonitoringLevel` is an `IntEnum` that controls collection granularity.
Higher levels include everything from the previous ones.

| Level | Value | Emitted labels | Extra fields in ExecutionRecord |
|-------|-------|----------------|----------------------------------|
| OFF | 0 | none (zero overhead) | -- |
| BASIC | 10 | `use_case`, `value_track` | spans |
| STANDARD | 20 | + `subtrack` | spans |
| DETAILED | 30 | + `feature` | spans, tags, attributes in spans |
| DIAGNOSTIC | 40 | + `feature` | spans, tags, extra, mapping_source, dropped_spans, start_ns/end_ns in spans |

```python
from forge_base.pulse import MonitoringLevel

# Direct comparison (IntEnum)
assert MonitoringLevel.DETAILED >= MonitoringLevel.STANDARD

# OFF: runner calls execute() directly, no instrumentation
# BASIC: metrics with {use_case, value_track}
# STANDARD: adds {subtrack} to labels
# DETAILED: adds {feature}, saves tags and span attributes
# DIAGNOSTIC: includes extra, mapping_source, dropped_spans, span timestamps
```

### Example: choosing the level

```python
from forge_base.application import UseCaseBase
from forge_base.testing.fakes import FakeMetricsCollector
from forge_base.pulse import BasicCollector, MonitoringLevel, UseCaseRunner

class PingInput:
    pass

class PingOutput:
    def __init__(self, ok: bool = True) -> None:
        self.ok = ok

class PingUseCase(UseCaseBase[PingInput, PingOutput]):
    def _before_execute(self) -> None:
        pass
    def _after_execute(self) -> None:
        pass
    def _on_error(self, error: Exception) -> None:
        pass
    def execute(self, input_dto: PingInput) -> PingOutput:
        return PingOutput()

# STANDARD: labels include subtrack
metrics = FakeMetricsCollector()
collector = BasicCollector(metrics=metrics, level=MonitoringLevel.STANDARD)
runner = UseCaseRunner(
    use_case=PingUseCase(),
    level=MonitoringLevel.STANDARD,
    collector=collector,
)
runner.run(PingInput())

snapshot = collector.snapshot()
print(snapshot.level)  # MonitoringLevel.STANDARD
```

---

## 2. Mapping Hierarchy

The runner resolves context (value_track, subtrack, feature) in 4 layers,
each one able to override the previous:

| Priority | Source | mapping_source |
|----------|--------|----------------|
| 1 (base) | Heuristic (module/class) | `"heuristic"` |
| 2 | `@pulse_meta` decorator | `"decorator"` |
| 3 | `ValueTrackRegistry` (YAML) | `"spec"` |
| 4 (top) | `ctx_overrides` in `run()` | passed value |

```python
from forge_base.pulse import (
    BasicCollector, MonitoringLevel, UseCaseRunner,
    pulse_meta, ValueTrackRegistry,
)
from forge_base.testing.fakes import FakeMetricsCollector

# Layer 1: heuristic extracts use_case_name from class, feature from module
# Layer 2: @pulse_meta overrides subtrack, feature, value_track
# Layer 3: registry.resolve() overrides if found in YAML
# Layer 4: runner.run(input, value_track="override") overrides everything

metrics = FakeMetricsCollector()
collector = BasicCollector(metrics=metrics, level=MonitoringLevel.BASIC)
runner = UseCaseRunner(
    use_case=PingUseCase(),
    level=MonitoringLevel.BASIC,
    collector=collector,
)

# Override at run(): layer 4 overrides everything
runner.run(PingInput(), value_track="checkout", subtrack="payment")
```

### Viewing the mapping_source

With `DIAGNOSTIC`, the snapshot includes `mapping_source` in each execution:

```python
metrics = FakeMetricsCollector()
collector = BasicCollector(metrics=metrics, level=MonitoringLevel.DIAGNOSTIC)
runner = UseCaseRunner(
    use_case=PingUseCase(),
    level=MonitoringLevel.DIAGNOSTIC,
    collector=collector,
)
runner.run(PingInput())

snapshot = collector.snapshot()
print(snapshot.executions[0]["mapping_source"])  # "heuristic"
```

---

## 3. @pulse_meta

Class decorator that defines static observability metadata.
Does not alter execution -- only registers information.

```python
from forge_base.pulse import pulse_meta, read_pulse_meta

@pulse_meta(
    subtrack="billing",
    feature="invoices",
    value_track="checkout",
    tags={"team": "payments", "tier": "critical"},
)
class GenerateInvoiceUseCase(UseCaseBase[PingInput, PingOutput]):
    def _before_execute(self) -> None:
        pass
    def _after_execute(self) -> None:
        pass
    def _on_error(self, error: Exception) -> None:
        pass
    def execute(self, input_dto: PingInput) -> PingOutput:
        return PingOutput()
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `subtrack` | `str` | `""` | Overrides heuristic subtrack |
| `feature` | `str` | `""` | Overrides heuristic feature |
| `value_track` | `str` | `""` | Overrides value_track (default `"legacy"`) |
| `tags` | `dict[str, str]` | `None` | Static tags, frozen in `MappingProxyType` |

### Reading metadata programmatically

```python
meta = read_pulse_meta(GenerateInvoiceUseCase)
if meta:
    print(meta.subtrack)     # "billing"
    print(meta.value_track)  # "checkout"
    print(dict(meta.tags))   # {"team": "payments", "tier": "critical"}
```

---

## 4. ValueTrackRegistry (YAML)

Centralized mapping of UseCases to value tracks via YAML.
Higher priority than `@pulse_meta`, lower than overrides in `run()`.

### Spec schema 0.1

```yaml
schema_version: "0.1"

value_tracks:
  checkout:
    description: "Purchase flow"
    usecases:
      - GenerateInvoiceUseCase
      - ApplyDiscountUseCase
    subtracks:
      billing:
        - GenerateInvoiceUseCase
      pricing:
        - ApplyDiscountUseCase
    tags:
      domain: "commerce"
```

**Schema rules:**

- `schema_version`: required, only `"0.1"` supported
- `value_tracks`: non-empty dict
- Each track needs `usecases` (non-empty list, no duplicates)
- `subtracks`: optional, each UC must exist in the track's `usecases` list
- `tags`: optional, `dict[str, str]`
- `description`: optional

### Loading and using

```python
from pathlib import Path
from forge_base.pulse import ValueTrackRegistry

registry = ValueTrackRegistry()
registry.load_from_yaml(Path("pulse_spec.yaml"))

# Resolve by class name
mapping = registry.resolve("GenerateInvoiceUseCase")
if mapping:
    print(mapping.value_track)    # "checkout"
    print(mapping.subtrack)       # "billing"
    print(mapping.mapping_source) # "spec"
    print(dict(mapping.tags))     # {"domain": "commerce"}
```

### Loading from dict (without file)

```python
registry = ValueTrackRegistry()
registry.load_from_dict({
    "schema_version": "0.1",
    "value_tracks": {
        "onboarding": {
            "usecases": ["RegisterUserUseCase"],
        }
    }
})
```

### Integrating with UseCaseRunner

```python
runner = UseCaseRunner(
    use_case=GenerateInvoiceUseCase(),
    level=MonitoringLevel.STANDARD,
    collector=collector,
    registry=registry,
)
# The runner calls registry.resolve() automatically on each run()
```

---

## 5. Tags

Tags are key-value pairs that enrich the execution context.
Two sources are merged by the runner:

| Priority | Source | When |
|----------|--------|------|
| 1 (base) | `@pulse_meta(tags={...})` | Runner init |
| 2 (top) | `runner.run(..., tags={...})` | Each call |

Runtime tags override decorator tags in case of key conflict.

> **Note:** Tags defined in the YAML spec are available in the
> `ValueTrackMapping` object (via `mapping.tags`), but are **not** merged
> automatically into `ExecutionContext.tags` by the runner.

### Level gating

Tags only appear in the `ExecutionRecord` and snapshot starting from
`DETAILED` (30). At lower levels, tags are ignored in the output.

```python
@pulse_meta(tags={"team": "platform"})
class TaggedUseCase(UseCaseBase[PingInput, PingOutput]):
    def _before_execute(self) -> None:
        pass
    def _after_execute(self) -> None:
        pass
    def _on_error(self, error: Exception) -> None:
        pass
    def execute(self, input_dto: PingInput) -> PingOutput:
        return PingOutput()

metrics = FakeMetricsCollector()
collector = BasicCollector(metrics=metrics, level=MonitoringLevel.DETAILED)
runner = UseCaseRunner(
    use_case=TaggedUseCase(),
    level=MonitoringLevel.DETAILED,
    collector=collector,
)

# Runtime tags merge with decorator tags
runner.run(PingInput(), tags={"env": "staging", "team": "checkout"})

snapshot = collector.snapshot()
tags = snapshot.executions[0]["tags"]
print(dict(tags))
# {"team": "checkout", "env": "staging"}
# "team" came from runtime, overriding the decorator
```

---

## 6. pulse_span

Context manager for measuring internal sections of `execute()`.
Creates `SpanRecord` with duration, supports nesting and attributes.

### Basic

```python
from forge_base.pulse import pulse_span

class ProcessOrderUseCase(UseCaseBase[PingInput, PingOutput]):
    def _before_execute(self) -> None:
        pass
    def _after_execute(self) -> None:
        pass
    def _on_error(self, error: Exception) -> None:
        pass

    def execute(self, input_dto: PingInput) -> PingOutput:
        with pulse_span("validate_order"):
            pass  # validation

        with pulse_span("charge_payment", provider="stripe"):
            pass  # charge

        return PingOutput()
```

### No-op outside the runner

```python
# Calling pulse_span outside an active UseCaseRunner is safe:
# yields None, zero overhead
with pulse_span("noop") as span:
    assert span is None
```

### Nesting (parent-child)

Nested spans receive `parent_span_id` automatically:

```python
class NestedSpanUseCase(UseCaseBase[PingInput, PingOutput]):
    def _before_execute(self) -> None:
        pass
    def _after_execute(self) -> None:
        pass
    def _on_error(self, error: Exception) -> None:
        pass

    def execute(self, input_dto: PingInput) -> PingOutput:
        with pulse_span("parent"):
            with pulse_span("child_a"):
                pass
            with pulse_span("child_b"):
                pass
        return PingOutput()

metrics = FakeMetricsCollector()
collector = BasicCollector(metrics=metrics, level=MonitoringLevel.BASIC)
runner = UseCaseRunner(
    use_case=NestedSpanUseCase(),
    level=MonitoringLevel.BASIC,
    collector=collector,
)
runner.run(PingInput())

spans = collector.snapshot().executions[0]["spans"]
parent = [s for s in spans if s["name"] == "parent"][0]
child_a = [s for s in spans if s["name"] == "child_a"][0]

assert child_a["parent_span_id"] == parent["span_id"]
```

### Attributes in spans

Kwargs passed to `pulse_span` become `attributes` in the SpanRecord.
Visible in the snapshot only from `DETAILED` onwards:

```python
with pulse_span("http_call", method="POST", url="/api/charge"):
    pass  # HTTP call

# In the snapshot with DETAILED+:
# {"name": "http_call", "attributes": {"method": "POST", "url": "/api/charge"}, ...}
```

### Timestamps (DIAGNOSTIC)

In `DIAGNOSTIC`, spans include `start_ns` and `end_ns` (nanoseconds):

```python
# With DIAGNOSTIC:
# {"name": "http_call", "start_ns": 123456789, "end_ns": 123457000, ...}
```

---

## 7. BudgetPolicy

Limits the number of spans per execution, preventing data explosion
in UseCases with many iterations.

```python
from forge_base.pulse import BudgetPolicy

budget = BudgetPolicy(
    max_spans_per_execution=10,   # maximum 10 spans (default: 64)
    max_events_per_execution=128, # reserved for future use
)
```

### Usage with runner

```python
class LoopyUseCase(UseCaseBase[PingInput, PingOutput]):
    def _before_execute(self) -> None:
        pass
    def _after_execute(self) -> None:
        pass
    def _on_error(self, error: Exception) -> None:
        pass

    def execute(self, input_dto: PingInput) -> PingOutput:
        for i in range(50):
            with pulse_span(f"step_{i}"):
                pass
        return PingOutput()

metrics = FakeMetricsCollector()
collector = BasicCollector(metrics=metrics, level=MonitoringLevel.DIAGNOSTIC)
runner = UseCaseRunner(
    use_case=LoopyUseCase(),
    level=MonitoringLevel.DIAGNOSTIC,
    collector=collector,
    budget=BudgetPolicy(max_spans_per_execution=5),
)
runner.run(PingInput())

snapshot = collector.snapshot()
record = snapshot.executions[0]
print(len(record["spans"]))     # 5
print(record["dropped_spans"])  # 45 (visible in DIAGNOSTIC)
```

When the budget is reached, `pulse_span` returns `None` (no-op) -- it does
not raise an exception.

---

## 8. SamplingPolicy

Controls the sampling rate to reduce data volume.
Three levels of specificity:

```python
from forge_base.pulse import SamplingPolicy

policy = SamplingPolicy(
    default_rate=0.5,  # 50% of all executions
    by_value_track={"checkout": 1.0, "analytics": 0.1},
    by_tenant={"tenant_vip": 1.0},
)
```

### Resolution (most specific wins)

1. `by_tenant` -- checks `ctx.extra["tenant"]`
2. `by_value_track` -- checks `ctx.value_track`
3. `default_rate` -- fallback

```python
# All checkout executions are sampled (1.0)
# VIP tenant always sampled regardless of track
# Others: 50% chance

metrics = FakeMetricsCollector()
collector = BasicCollector(metrics=metrics, level=MonitoringLevel.BASIC)
runner = UseCaseRunner(
    use_case=PingUseCase(),
    level=MonitoringLevel.BASIC,
    collector=collector,
    policy=policy,
)
```

### Using tenant in sampling

For `by_tenant` to work, pass `tenant` via `extra` in `run()`.
The `extra` dict goes through `redact_keys` automatically -- avoid keys
with sensitive names (like `api_key`) if you need to read them later.

```python
runner.run(PingInput(), extra={"tenant": "tenant_vip"})
```

### Valid rates

- `1.0` -- always sampled
- `0.0` -- never sampled (basic metrics are still emitted)
- `0.0 < rate < 1.0` -- probabilistic (`random.random() < rate`)

---

## 9. ExportPipeline

Asynchronous pipeline to export `ExecutionRecord` via buffer + exporter.

### Components

| Class | Role |
|-------|------|
| `AsyncBuffer` | Thread-safe queue with drop policy |
| `JsonLinesExporter` | Writes JSON Lines to a stream |
| `InMemoryExporter` | Stores `(context, data)` tuples in a list |
| `ExportPipeline` | Orchestrates buffer + exporter via `flush()` |

### AsyncBuffer

```python
from forge_base.pulse import AsyncBuffer

buffer = AsyncBuffer(
    max_size=10_000,       # capacity (default: 10_000)
    drop_policy="oldest",  # "oldest" (evict) or "newest" (reject)
)

# Push is synchronous (used by the collector)
# buffer.push(record) -> bool

print(buffer.size)        # items in buffer
print(buffer.drop_count)  # total drops since creation
```

### JsonLinesExporter

Writes each record as a compact JSON line:

```python
import io
from forge_base.pulse import JsonLinesExporter

stream = io.StringIO()
exporter = JsonLinesExporter(stream=stream)

# After flush:
# stream.getvalue() contains JSON lines separated by \n
```

### InMemoryExporter

Useful for tests -- stores records in memory:

```python
from forge_base.pulse import InMemoryExporter

exporter = InMemoryExporter()

# After flush:
for ctx, data in exporter.records:
    print(data["use_case_name"], data["duration_ms"])
```

### Complete pipeline

```python
import asyncio
import io
from forge_base.pulse import (
    AsyncBuffer,
    BasicCollector,
    ExportPipeline,
    JsonLinesExporter,
    MonitoringLevel,
    UseCaseRunner,
)
from forge_base.testing.fakes import FakeMetricsCollector

metrics = FakeMetricsCollector()
collector = BasicCollector(metrics=metrics, level=MonitoringLevel.BASIC)
runner = UseCaseRunner(
    use_case=PingUseCase(),
    level=MonitoringLevel.BASIC,
    collector=collector,
)

# Execute a few times
for _ in range(5):
    runner.run(PingInput())

# Set up pipeline
stream = io.StringIO()
buffer = AsyncBuffer(max_size=1000)
pipeline = ExportPipeline(buffer=buffer, exporter=JsonLinesExporter(stream=stream))

# Transfer records to the buffer
# Note: _records is an internal attribute of BasicCollector.
# In production, connect the buffer directly to the collector
# or use a custom collector that pushes to the buffer.
for record in collector._records:
    buffer.push(record)

# Asynchronous flush
async def export():
    count = await pipeline.flush()
    print(f"Exported: {count} records")
    print(stream.getvalue()[:200])

asyncio.run(export())
```

---

## 10. DashboardSummary

Aggregates data from a `PulseSnapshot` into dashboard metrics:
total executions, error rate, mean duration, p95, top error types.

```python
from forge_base.pulse import DashboardSummary

snapshot = collector.snapshot()
summary = DashboardSummary.from_snapshot(snapshot, top_n=5)

print(f"Total: {summary.total_executions}")
print(f"Successful: {summary.successful}")
print(f"Failed: {summary.failed}")
print(f"Error rate: {summary.error_rate:.2%}")
print(f"Mean duration: {summary.mean_duration_ms:.2f}ms")
print(f"Top errors: {summary.top_error_types}")
```

### TrackSummary (per value track)

```python
for track in summary.by_value_track:
    print(
        f"  {track.value_track}: "
        f"{track.total_executions} exec, "
        f"p95={track.p95_duration_ms:.2f}ms, "
        f"err={track.error_rate:.2%}"
    )
```

### Complete structure

```python
from forge_base.pulse import DashboardSummary, TrackSummary

# DashboardSummary fields:
#   total_executions: int
#   successful: int
#   failed: int
#   error_rate: float
#   mean_duration_ms: float
#   top_error_types: tuple[tuple[str, int], ...]
#   by_value_track: tuple[TrackSummary, ...]

# TrackSummary fields:
#   value_track: str
#   total_executions: int
#   successful: int
#   failed: int
#   error_rate: float
#   mean_duration_ms: float
#   p95_duration_ms: float
```

---

## 11. ECM

`ExtensionCompatibilityMatrix` validates whether third-party extensions are
compatible with the current ForgePulse version.

```python
from forge_base.pulse import ExtensionCompatibilityMatrix, PULSE_SCHEMA_VERSION

ecm = ExtensionCompatibilityMatrix()

# Register extensions with the minimum ForgePulse version they require
ecm.register_extension(
    name="forge-otel-bridge",
    version="1.2.0",
    requires_pulse="0.3",
)
ecm.register_extension(
    name="forge-sentry",
    version="2.0.0",
    requires_pulse="0.4",  # future version
)
```

### Validation

```python
# List incompatible ones
issues = ecm.validate(PULSE_SCHEMA_VERSION)
for issue in issues:
    print(f"{issue.name} v{issue.version}: requires pulse {issue.requires_pulse}, current {issue.actual_pulse}")

# Raise if there are incompatibilities
from forge_base.pulse import PulseIncompatibleExtensionError
try:
    ecm.validate_or_raise(PULSE_SCHEMA_VERSION)
except PulseIncompatibleExtensionError as e:
    print(e)

# Warning (non-blocking)
issues = ecm.validate_or_warn(PULSE_SCHEMA_VERSION)
```

### Compatibility rules

- Major must be equal
- Pulse minor must be `>=` the one required by the extension
- Accepted formats: `"major.minor"` or `"major.minor.patch"`

---

## 12. Redaction

`redact_keys` replaces values of sensitive keys with `"[REDACTED]"`.
Called automatically by `ExecutionContext.build()` on the `extra` dict.

```python
from forge_base.pulse import redact_keys

data = {
    "user_id": "123",
    "password": "s3cr3t",
    "api_key": "ak_live_xxx",
    "request_url": "/api/users",
    "auth_token": "bearer_abc",
}

clean = redact_keys(data)
print(clean)
# {
#   "user_id": "123",
#   "password": "[REDACTED]",
#   "api_key": "[REDACTED]",
#   "request_url": "/api/users",
#   "auth_token": "[REDACTED]",
# }
```

### Detected patterns

| Pattern | Example match |
|---------|--------------|
| `password` | `password`, `user_password` |
| `secret` | `client_secret` |
| `token` | `access_token` |
| `api_key` / `api-key` | `api_key`, `api-key` |
| `auth_token` / `auth_key` / `auth_secret` / `auth_header` / `auth_cookie` / `auth_code` / `auth_hash` | `auth_token` |
| `credential` | `db_credential` |
| `private_key` / `private-key` | `private_key` |
| `ssn` | `ssn`, `user_ssn` |
| `credit_card` / `credit-card` | `credit_card` |

Detection is case-insensitive.

---

## 13. Testing with FakeMetricsCollector

`FakeMetricsCollector` is an in-memory collector for tests.
Satisfies `PulseMetricsProtocol`.

```python
from forge_base.testing.fakes import FakeMetricsCollector

metrics = FakeMetricsCollector()
```

### Built-in assertions

```python
from forge_base.pulse import BasicCollector, MonitoringLevel, UseCaseRunner

metrics = FakeMetricsCollector()
collector = BasicCollector(metrics=metrics, level=MonitoringLevel.BASIC)
runner = UseCaseRunner(
    use_case=PingUseCase(),
    level=MonitoringLevel.BASIC,
    collector=collector,
)

runner.run(PingInput())

# Check that counter was incremented
assert metrics.was_incremented("pulse.execution.count")

# Check exact value
metrics.assert_counter_equals(
    "pulse.execution.count",
    1,
    use_case="PingUseCase",
    value_track="legacy",
)

# Check that duration was recorded
assert metrics.was_recorded("pulse.execution.duration_ms")

# Access values directly
count = metrics.get_counter(
    "pulse.execution.count",
    use_case="PingUseCase",
    value_track="legacy",
)
assert count == 1

# Check that counter is greater than N
metrics.assert_counter_greater(
    "pulse.execution.count",
    0,
    use_case="PingUseCase",
    value_track="legacy",
)
```

### Complete report

```python
report = metrics.report()
print(report["counters"])     # {"pulse.execution.count{...}": 1, ...}
print(report["gauges"])       # {}
print(report["histograms"])   # {"pulse.execution.duration_ms{...}": {"count": 1, ...}}
```

### SpyCollector pattern

For tests that need to capture the collector's calls:

```python
class SpyCollector:
    def __init__(self) -> None:
        self.starts: list = []
        self.successes: list = []
        self.errors: list = []
        self.finishes: list = []

    def on_start(self, ctx):
        self.starts.append(ctx)

    def on_success(self, ctx, result):
        self.successes.append((ctx, result))

    def on_error(self, ctx, error):
        self.errors.append((ctx, error))

    def on_finish(self, ctx):
        self.finishes.append(ctx)

spy = SpyCollector()
runner = UseCaseRunner(
    use_case=PingUseCase(),
    level=MonitoringLevel.BASIC,
    collector=spy,
)
runner.run(PingInput())

assert len(spy.starts) == 1
assert len(spy.successes) == 1
assert spy.starts[0].use_case_name == "PingUseCase"
```

### Reset between tests

```python
metrics.clear()   # clears all counters, gauges, histograms
metrics.reset()   # alias for clear()
collector.clear_records()  # clears records from BasicCollector
```

---

## 14. Quick Reference

### Imports

```python
from forge_base.pulse import (
    # Core
    MonitoringLevel,
    UseCaseRunner,
    BasicCollector,
    PulseSnapshot,
    ExecutionRecord,

    # Context
    ExecutionContext,
    get_context,

    # Metadata
    pulse_meta,
    read_pulse_meta,

    # Value Tracks
    ValueTrackRegistry,
    ValueTrackMapping,

    # Spans
    pulse_span,
    SpanRecord,

    # Policies
    BudgetPolicy,
    SamplingPolicy,

    # Export
    ExportPipeline,
    AsyncBuffer,
    JsonLinesExporter,
    InMemoryExporter,

    # Dashboard
    DashboardSummary,
    TrackSummary,

    # Governance
    ExtensionCompatibilityMatrix,

    # Utilities
    redact_keys,
    PulseFieldNames,
    PULSE_SCHEMA_VERSION,

    # Protocols
    PulseCollector,
    PulseMetricsProtocol,
    PulseExporterProtocol,

    # Exceptions
    PulseError,
    PulseConfigError,
    PulseIncompatibleExtensionError,
)

from forge_base.testing.fakes import FakeMetricsCollector
```

### Cheat-sheet

| What you want | How to do it |
|---------------|-------------|
| Monitor a UseCase | `UseCaseRunner(uc, level=BASIC, collector=collector)` |
| Emit metrics | `BasicCollector(metrics, level=...)` |
| Take a snapshot | `collector.snapshot()` |
| Define metadata | `@pulse_meta(subtrack=..., feature=..., value_track=..., tags={...})` |
| Map via YAML | `registry.load_from_yaml(path)` + pass to runner |
| Measure internal section | `with pulse_span("name", **attrs): ...` |
| Limit spans | `BudgetPolicy(max_spans_per_execution=N)` |
| Sample executions | `SamplingPolicy(default_rate=0.5, by_value_track={...})` |
| Export JSON Lines | `ExportPipeline(AsyncBuffer(), JsonLinesExporter(stream))` |
| Aggregated dashboard | `DashboardSummary.from_snapshot(snapshot)` |
| Validate extensions | `ecm.register_extension(...)` + `ecm.validate_or_raise(version)` |
| Clean sensitive data | `redact_keys(data)` |
| Test without infra | `FakeMetricsCollector()` + `BasicCollector` |
| Override at run() | `runner.run(input, value_track=..., tags={...}, extra={...})` |
| View current context | `from forge_base.pulse import get_context; ctx = get_context()` |

### Metrics emitted by BasicCollector

| Metric | Type | When |
|--------|------|------|
| `pulse.execution.count` | counter | on_start |
| `pulse.execution.duration_ms` | histogram | on_finish |
| `pulse.execution.errors` | counter | on_error |
| `pulse.execution.success` | counter | on_success |
