# Formal Proposal — ForgeBase Evolution with CL/CE and Optional ForgePulse Layer (ValueTracks)

## 1) Context and Motivation

ForgeBase is currently used successfully without the formal concepts of **ValueTracks** and without an explicit boundary between **stable core** and **customer/product extensions**. This works for delivery but limits three strategic objectives:

1. **Objectively measuring value delivery**
   Without ValueTracks, we measure loose "technical health" (logs/metrics), but don't measure "value delivered per axis" (e.g., Cost Governance, Reliability, Security, Routing Quality). Result: the roadmap becomes narrative.

2. **Standardizing instrumentation for dev + agent**
   We want developers and agents to implement features already following patterns that facilitate measuring performance/cost/quality/complexity/security per ValueTrack. Without a native standard, each team measures in its own way — and comparison becomes impossible.

3. **Evolving in production with governance (without breaking core)**
   Instrumentation needs to be configurable by levels (like logs), by tenant, by ValueTrack, with sampling and budgets. This is an extension (CE), and should not contaminate the core (CL).

**Principle:** if a ValueTrack is not measurable, it becomes a slogan.

---

## 2) CL/CE: What It Is, and Why It Guides the Change

### CL — Core Logic (stable core)

Everything that must remain reliable, consistent, and compatible over time:

* Execution runtime (engine)
* Contracts (interfaces/types) and base schema
* Context propagation (correlation_id, tenant, version)
* Plugin/hook mechanisms and governance
* Backward compatibility and versioning

**CL must not contain** customer-specific rules, specific policies, or specific exporters.

### CE — Customer Extensions (configurable extensions)

Everything that varies by project/tenant/product/environment and must be pluggable:

* ValueTrack/SubTrack mappings to UseCases (via spec)
* Monitoring policies (level, sampling, budgets)
* Exporters/sinks (OTEL/Prometheus/ClickHouse/Postgres/file/etc.)
* Custom reports by product/customer
* Risk classifications and security tags

**CE cannot break through CL. CE plugs in via contract.**

### Why This Requires Changes to ForgeBase

Because today there is no **official point** in CL to:

* Load a consistent **ExecutionContext**
* Emit events/metrics/traces with a stable schema
* Apply policy by levels with a fast-path
* Allow CE to attach exporters/mappings/reports without touching the core

Without this, each product creates "side" instrumentation — duplicated, inconsistent, and hard to govern.

---

## 3) Objective of the Change

Add to ForgeBase an **optional layer** called **ForgePulse**, which instruments executions by ValueTrack **without breaking compatibility**, preserving Clean Architecture and enabling CL/CE governance.

**Important:** this does not replace the current ForgeBase. It is a **runtime extension** that can be turned off (OFF) and enabled by levels.

---

## 4) Premises and Constraints

* **Full compatibility**: the current ForgeBase must continue working without any consumer code changes.
* **Opt-in**: no "mandatory decorator". Decorators (if they exist) are optional metadata.
* **Clean Architecture intact**: UseCases do not depend on exporters, OTEL, databases, etc. Instrumentation occurs in the composition root and adapters.
* **Controlled overhead**: levels + sampling + budgets + buffer/drop.
* **Stable schema**: events/metrics/traces follow versioning and compatibility.

---

## 5) Solution Overview: ForgePulse as an Optional Shell

### Components (high level)

**ForgeBase (existing CL)**
-> remains as the engine

**ForgePulse (optional CL)**
-> instrumentation runtime: context, policy, collectors, reporter

**ForgePulse Extensions (CE)**
-> mappings (spec), exporters, specific policies, custom reports

### Where Instrumentation Happens (to maintain Clean Architecture)

* **UseCaseRunner/ExecutionRunner** (composition root): measures start/end/error, creates context
* **Adapters** (LLM/HTTP/DB): measure cost/latency/retry/fallback and generate spans/events
* UseCase remains "pure"

---

## 6) Universal ExecutionContext (even in legacy)

ForgePulse introduces `ExecutionContext` as **always present**, even if the code does not declare a ValueTrack.

Minimum fields:

* `correlation_id`
* `tenant_id`
* `value_track`
* `subtrack`
* `feature`
* `use_case`
* `version` (build/git sha)
* `environment` (dev/stg/prod)

### Legacy Fallback (compatibility)

If there is no mapping or decorators:

* `value_track="legacy"`
* `subtrack="legacy"`
* `feature/use_case` inferred from class/module/route

**Result:** legacy becomes observable without refactoring.

---

## 7) Monitoring Levels (policy) and Performance Control

ForgePulse must support:

* **OFF**: real no-op (fast path)
* **BASIC**: total time + success/error + counters
* **STANDARD**: + latency per adapter + errors per stage (sampled)
* **DETAILED**: + tracing + cost (tokens/cpu) (aggressive sampling)
* **DIAGNOSTIC**: profiling/redacted payload (only by flag/tenant/correlation_id)

Mandatory rules:

* **Decide level before** allocating/serializing
* Sampling by `value_track`, `tenant`, `endpoint`
* Budgets per execution (span/event/byte limits)
* Async buffer + controlled drop (don't crash the system due to telemetry)

---

## 8) ValueTracks/SubTracks: How to Map Without Forcing the Team

Resolution order (priority):

1. **Spec/Registry (CE)** — recommended (doesn't touch code)
2. **Optional decorators (metadata only)** — when it makes sense
3. **Legacy heuristic** — fallback

Example (CE) `forgepulse.value_tracks.yml`:

* Maps `use_case` -> `value_track`/`subtrack`
* Allows tags (domain, risk, etc.)

This enables gradual and governed adoption.

---

## 9) ECM — Extension Compatibility Matrix (extension governance)

### What Is ECM

ECM is the formal compatibility matrix between:

* ForgeBase version (CL)
* ForgePulse Schema version (CL)
* Extension versions (CE): exporters, mapping packages, reporters

**Purpose:** prevent an incompatible CE extension from entering production by accident.

### Expected Behavior

* On startup: runtime validates ECM
* If incompatible: disables the extension (or hard fails, per policy)
* Logs incompatibility event/alert

---

## 10) Reports (minimum outputs)

ForgePulse must generate, at minimum:

### Operational Report (technical)

* Top ValueTracks by latency (p95/p99)
* Top by error rate
* Bottlenecks by adapter/subtrack (when available)
* Regression vs baseline by version

### Strategic Report (product/executive)

* Cost per ValueTrack (tokens/CPU when enabled)
* Adoption/usage per ValueTrack and per tenant
* Complexity proxy (spans/subtracks/external calls)
* Exposure/risk (policy denies, invalid accesses, etc.)

Format: **Markdown + JSON**.

---

## 11) Acceptance Criteria

1. With ForgePulse **OFF**, the entire current ForgeBase runs identically (tests pass).
2. In **BASIC**, overhead is minimal and does not create a noticeable bottleneck.
3. `ExecutionContext` always exists (even legacy with `legacy/*`).
4. Policy works: levels, sampling, budgets, toggles by tenant/correlation_id.
5. ECM is validated and prevents incompatible extensions.
6. Reports generated (operational + strategic) at least for `legacy` and for mapped tracks.
7. Clean Architecture preserved: use cases do not depend on infrastructure.

---

## 12) Adoption Plan (trauma-free)

* **Phase 0**: integrate ForgePulse as no-op (OFF)
* **Phase 1**: enable BASIC/STANDARD with legacy heuristic -> first reports
* **Phase 2**: add mapping via spec (CE) -> real ValueTracks without touching code
* **Phase 3**: optional decorators in new modules -> subtrack/trace precision
* **Phase 4**: strict mode per scope (only where controlled)

---

## 13) Direct Benefits (why it's worth the effort)

* Roadmap stops being narrative: becomes evidence per ValueTrack
* Agents and developers code within measurable patterns
* CL/CE governance prevents "coupled telemetry" and product-specific hacks
* Quick diagnosis with levels (microscope when needed, lightweight day-to-day)
* Version comparison and regression detection becomes routine, not a hunt
