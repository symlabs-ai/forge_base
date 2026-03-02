# ADR-008: ForgePulse CL/CE Separation

**Status:** Accepted
**Date:** 2026-03-02
**Context:** ForgeBase 0.3.0

## Decision

ForgePulse is implemented as `forge_base.pulse`, a subpackage within ForgeBase that provides
optional per-ValueTrack instrumentation with a clear CL/CE (Core Library / Customer Extension)
separation.

### CL (Core Library) — ships with ForgeBase

- `MonitoringLevel` enum (OFF/BASIC/STANDARD/DETAILED/DIAGNOSTIC)
- `ExecutionContext` frozen dataclass with `ContextVar` propagation
- `PulseCollector` protocol and `NoOpCollector`
- `UseCaseRunner` with fast-path for OFF level
- `PulseMetricsProtocol` (satisfied by existing `TrackMetrics` and `FakeMetricsCollector`)
- `PulseFieldNames` (standardized dot-namespace field naming contract)
- `redact_keys()` for sensitive data masking

### CE (Customer Extension) — defined by derived apps

- Concrete `PulseCollector` implementations
- `PulseExporterProtocol` implementations (exporters to external systems)
- YAML-based ValueTrack specs (Phase 2+)
- Custom field mappings and sampling policies

## Rationale

- ForgeBase measures "technical health" but not "value delivered per axis"
- CL provides the structural foundation; CE provides the semantic mapping
- Zero overhead when `MonitoringLevel.OFF` (fast-path: direct `execute()` call)
- No changes to existing ForgeBase modules — pulse is additive-only
- Existing `TrackMetrics` and `FakeMetricsCollector` satisfy `PulseMetricsProtocol` without modification

## Consequences

- New code can opt into pulse instrumentation by using `UseCaseRunner`
- Existing code continues working unchanged
- Architecture boundaries enforced via import-linter contracts
- `pulse/` cannot import from `domain/`, `infrastructure/`, or `adapters/`
- No existing layer can import from `pulse/`
