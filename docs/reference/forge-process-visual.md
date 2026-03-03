# ForgeProcess: Complete Visual Guide

**Learn the cognitive cycle through diagrams, examples, and practical visualizations.**

---

## Visual Index

1. [The Complete Cycle (Macro Diagram)](#complete-cycle)
2. [Phase 1: MDD (Market Driven)](#phase-1-mdd)
3. [Critical Transition: MDD → BDD](#transition-mdd-bdd)
4. [Phase 2: BDD (Behavior Driven)](#phase-2-bdd)
5. [Phase 3: TDD (Test Driven)](#phase-3-tdd)
6. [Phase 4: CLI (Cognitive Interface)](#phase-4-cli)
7. [Phase 5: Feedback (Reflection)](#phase-5-feedback)
8. [Complete Example: From Value to Feedback](#complete-example)

---

<a name="complete-cycle"></a>
## The Complete Cycle (Macro Diagram)

```
                          FORGE PROCESS
                     ═══════════════════════

┌─────────────────────────────────────────────────────┐
│                                                     │
│  Phase 1: MDD (Market Driven Development)           │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━          │
│  QUESTION: "WHY should this system exist?"          │
│                                                     │
│  Artifact: forge.yaml                               │
│  Output: ValueTracks, Value KPIs                    │
│                                                     │
│  Example:                                           │
│    ValueTrack: "ProcessOrder"                       │
│    KPI: "< 2 minutes per order"                     │
│                                                     │
└──────────────────────┬──────────────────────────────┘
                       │
                       │ COGNITIVE TRANSLATION
                       │ (Value → Behavior)
                       ▼
┌─────────────────────────────────────────────────────┐
│                                                     │
│  Phase 2: BDD (Behavior Driven Development)         │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━          │
│  QUESTION: "WHAT does the system do?"               │
│                                                     │
│  Artifact: process_order.feature                    │
│  Output: Scenarios (Given/When/Then)                │
│                                                     │
│  Example:                                           │
│    Given a valid order                              │
│    When I process it                                │
│    Then it should complete in < 2 min               │
│                                                     │
└──────────────────────┬──────────────────────────────┘
                       │
                       │ TECHNICAL SPECIFICATION
                       ▼
┌─────────────────────────────────────────────────────┐
│                                                     │
│  Phase 3: TDD (Test Driven Development)             │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━          │
│  QUESTION: "HOW to implement? (with proof)"         │
│                                                     │
│  Artifact: test_process_order.py                    │
│  Output: Tested code                                │
│                                                     │
│  Example:                                           │
│    def test_should_process_in_2_minutes():          │
│        # Red → Green → Refactor                     │
│                                                     │
└──────────────────────┬──────────────────────────────┘
                       │
                       │ EXECUTABLE MANIFESTATION
                       ▼
┌─────────────────────────────────────────────────────┐
│                                                     │
│  Phase 4: CLI (Cognitive Interface)                 │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━          │
│  QUESTION: "Execute and observe?"                   │
│                                                     │
│  Artifact: forge_base CLI                           │
│  Output: Logs, Metrics, Traces                      │
│                                                     │
│  Example:                                           │
│    $ forge_base execute ProcessOrder                │
│    Duration: 1.8 minutes ✅                          │
│                                                     │
└──────────────────────┬──────────────────────────────┘
                       │
                       │ EVIDENCE COLLECTION
                       ▼
┌─────────────────────────────────────────────────────┐
│                                                     │
│  Phase 5: Feedback (Reflection)                     │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━          │
│  QUESTION: "Learn and adjust?"                      │
│                                                     │
│  Artifact: feedback_report.jsonl                    │
│  Output: Insights, Recommendations                  │
│                                                     │
│  Example:                                           │
│    KPI Target: < 2 min                              │
│    Actual: 1.8 min (✅ Met!)                         │
│    Recommendation: Maintain strategy                │
│                                                     │
└──────────────────────┬──────────────────────────────┘
                       │
                       │ LEARNING LOOP
                       └──────────────────┐
                                          │
                  ┌───────────────────────┘
                  ▼
         Back to MDD
       (Adjust forge.yaml)
```

---

<a name="phase-1-mdd"></a>
## Phase 1: MDD (Market Driven Development)

### Artifact Diagram

```
forge.yaml
├── project
│   ├── name
│   ├── vision
│   └── value_proposition
│
├── value_tracks                  ← Flows that deliver value
│   ├── ProcessOrder
│   │   ├── description
│   │   ├── value_metric
│   │   └── stakeholders
│   │
│   └── IssueInvoice
│       ├── description
│       ├── value_metric
│       └── stakeholders
│
├── support_tracks                ← Support flows
│   ├── ManageInventory
│   └── CalculateTaxes
│
└── kpis                          ← Value metrics
    ├── Order Processing Time
    └── Invoice Error Rate
```

### Complete Example: forge.yaml

```yaml
# forge.yaml
project:
  name: "EcommerceSystem"
  vision: "Facilitate online sales with agility and security"
  value_proposition:
    - "Process orders 50% faster"
    - "Zero errors in invoices"
    - "Real-time tracking"

value_tracks:
  - name: "ProcessOrder"
    description: "Process an order from start to finish"
    value_metric: "Average time < 2 minutes"
    stakeholders:
      - "Seller"
      - "Customer"
    business_value: "Increases conversion and satisfaction"

  - name: "IssueInvoice"
    description: "Issue invoices automatically"
    value_metric: "0% errors in calculation"
    stakeholders:
      - "Seller"
      - "Accountant"
    business_value: "Avoids tax fines"

support_tracks:
  - name: "ManageInventory"
    description: "Control inventory"
    supports: ["ProcessOrder"]

  - name: "CalculateTaxes"
    description: "Calculate taxes"
    supports: ["IssueInvoice"]

kpis:
  - metric: "Order Processing Time"
    target: "< 2 minutes"
    current: "4.5 minutes"
    priority: "critical"

  - metric: "Invoice Error Rate"
    target: "0%"
    current: "3.2%"
    priority: "high"
```

### Visualization: ValueTracks vs SupportTracks

```
VALUE TRACKS                SUPPORT TRACKS
(Deliver direct value)      (Support value tracks)

┌─────────────────┐         ┌─────────────────┐
│  ProcessOrder   │◄────────│ ManageInventory │
│  (VALUE)        │         │  (SUPPORT)      │
└─────────────────┘         └─────────────────┘
        │
        │ uses
        ▼
┌─────────────────┐         ┌─────────────────┐
│  IssueInvoice   │◄────────│  CalculateTaxes │
│  (VALUE)        │         │  (SUPPORT)      │
└─────────────────┘         └─────────────────┘
```

---

<a name="transition-mdd-bdd"></a>
## Critical Transition: MDD → BDD

**The moment where abstract thought becomes concrete action.**

### Translation Visualization

```
MDD (Abstract)                    BDD (Concrete)
══════════════                    ══════════════

ValueTrack:                       Feature:
"ProcessOrder"        ─────────>  "Process complete order"
                     translation
                                  Scenario:
Value Metric:                     "Given a valid order"
"< 2 minutes"         ─────────>  "When I process it"
                     specifies    "Then it completes in < 2 min"

Stakeholder:                      Actor:
"Seller"              ─────────>  "As a seller"
                     personifies

Business Value:                   Acceptance Criteria:
"Increases conversion" ─────────>  "Order processed successfully"
                     verifies     "Time recorded in metric"
```

### Side-by-Side Example

#### MDD (forge.yaml)
```yaml
value_tracks:
  - name: "CreateUser"
    description: "Fast and secure registration"
    value_metric: "95% complete in < 30s"
    stakeholders: ["New user"]
```

#### BDD (.feature)
```gherkin
Feature: Fast and secure user registration
  So that new users can get started quickly
  As a visitor
  I want to register easily

  Scenario: Successful registration
    Given I am on the registration page
    And I fill in valid data
    When I click "Create account"
    Then my account should be created
    And the process should take < 30 seconds
    And I should receive a confirmation email
```

#### Complete Mapping

| MDD | → | BDD |
|-----|---|-----|
| ValueTrack name | → | Feature title |
| description | → | Feature description |
| value_metric | → | Acceptance criteria (Then steps) |
| stakeholders | → | Actors (As a...) |
| business_value | → | So that... (benefit) |

---

<a name="phase-2-bdd"></a>
## Phase 2: BDD (Behavior Driven Development)

### Anatomy of a Feature File

```
┌────────────────────────────────────────────────────┐
│ Feature: [Behavior title]                          │  ← WHAT
│   [3-line narrative]                               │
│   So that [benefit]                                │  ← WHY
│   As a [actor]                                     │  ← WHO
│   I want [action]                                  │  ← WHAT
├────────────────────────────────────────────────────┤
│ Background:                                        │  ← Common context
│   Given [common precondition]                      │
├────────────────────────────────────────────────────┤
│ Scenario: [Specific case]                          │  ← Concrete example
│   Given [context]                                  │  ← Initial state
│   And [more context]                               │
│   When [action]                                    │  ← User action
│   Then [expected result]                           │  ← Behavior
│   And [additional verification]                    │  ← More checks
├────────────────────────────────────────────────────┤
│ Business Rules:                                    │  ← Documented rules
│   - [Rule 1]                                       │
│   - [Rule 2]                                       │
└────────────────────────────────────────────────────┘
```

### Visual Example: IssueInvoice

```gherkin
┌─────────────────────────────────────────────────────┐
│ Feature: Invoice issuance                            │
│   So that merchants can bill their sales             │
│   As a management system                             │
│   I should issue invoices automatically              │
├─────────────────────────────────────────────────────┤
│ Background:                                         │
│   Given system configured for NF-e                  │
│   And valid SEFAZ credentials                       │
├─────────────────────────────────────────────────────┤
│ Scenario: Successful issuance                        │
│                                                     │
│   ┌─────────────────────────────────────┐          │
│   │ GIVEN (Initial state)              │          │
│   │  - Valid order R$ 1000             │          │
│   │  - Customer with CPF              │          │
│   │  - Taxable product                │          │
│   └─────────────────────────────────────┘          │
│                ↓                                    │
│   ┌─────────────────────────────────────┐          │
│   │ WHEN (Action)                      │          │
│   │  - Issue invoice                   │          │
│   └─────────────────────────────────────┘          │
│                ↓                                    │
│   ┌─────────────────────────────────────┐          │
│   │ THEN (Expected result)             │          │
│   │  ✅ ICMS = R$ 180 (18%)            │          │
│   │  ✅ XML generated                  │          │
│   │  ✅ Log recorded                   │          │
│   │  ✅ Sent to SEFAZ                  │          │
│   │  ✅ DANFE sent by email            │          │
│   └─────────────────────────────────────┘          │
├─────────────────────────────────────────────────────┤
│ Business Rules:                                     │
│   1. Products must have a valid NCM                 │
│   2. ICMS per state tax table                       │
│   3. Sequential numbering required                  │
│   4. Automatic retry on failures (3x)               │
└─────────────────────────────────────────────────────┘
```

---

<a name="phase-3-tdd"></a>
## Phase 3: TDD (Test Driven Development)

### Red-Green-Refactor Cycle

```
RED Phase (Test fails)
┌────────────────────────────────┐
│ def test_icms_calculation():   │
│     usecase = IssueInvoice()   │
│     result = usecase.execute(  │
│         order_value=1000,      │
│         uf="SP"                │
│     )                          │
│     assert result.icms == 180  │  ← FAILS
│                                │     (code doesn't exist)
└────────────────────────────────┘
            ↓
GREEN Phase (Minimum code)
┌────────────────────────────────┐
│ class IssueInvoiceUseCase:     │
│     def execute(self, input):  │
│         icms = input.value *   │
│                0.18            │
│         return Output(         │
│             icms=icms          │
│         )                      │  ← PASSES
└────────────────────────────────┘
            ↓
REFACTOR Phase (Improvement)
┌────────────────────────────────┐
│ class IssueInvoiceUseCase:     │
│     ICMS_TABLE = {             │
│         "SP": 0.18,            │
│         "RJ": 0.20             │
│     }                          │
│                                │
│     def execute(self, input):  │
│         rate = self.ICMS_TABLE │
│                 [input.uf]     │
│         icms = input.value *   │
│                rate            │
│         return Output(         │
│             icms=icms          │
│         )                      │  ← PASSES (improved)
└────────────────────────────────┘
```

### BDD → TDD Mapping

```
BDD Scenario                          TDD Test
════════════════                      ═════════

Given an order of R$ 1000             order = Order(value=1000, uf="SP")
When I issue the invoice              result = usecase.execute(order)
Then ICMS should be R$ 180            assert result.icms == 180.00


BDD Scenario                          TDD Test
════════════════                      ═════════

Given product without NCM             product = Product(ncm=None)
When I try to issue the invoice       with pytest.raises(ValidationError):
Then it should reject                     usecase.execute(product)
```

### ForgeBase Test Pyramid

```
                    ▲
                   ╱ ╲
                  ╱   ╲
                 ╱  E2E ╲           ← 10% (few, slow)
                ╱ (CLI)  ╲
               ╱───────────╲
              ╱             ╲
             ╱  Integration  ╲      ← 20% (medium)
            ╱  (Repositories) ╲
           ╱───────────────────╲
          ╱                     ╲
         ╱      Unit Tests       ╲  ← 70% (many, fast)
        ╱     (UseCases)          ╲
       ╱───────────────────────────╲
```

---

<a name="phase-4-cli"></a>
## Phase 4: CLI (Cognitive Interface)

### Execution Flow via CLI

```
Terminal                  CLI               ForgeBase
════════                  ═══               ═════════

$ forge_base execute  ─────>  Parse command
  IssueInvoiceUseCase         │
  --input data.json           │
  --verbose                   ▼
                          Load UseCase
                              │
                              ▼
                          Inject dependencies
                              │
                              ▼
                          Enable metrics  ────> MetricsCollector
                              │
                              ▼
                          Enable tracing  ────> TracingService
                              │
                              ▼
                          Execute  ──────────> UseCase.execute()
                              │                      │
                              │                      ▼
                          Collect output        Business logic
                              │                      │
                              ◄──────────────────────┘
                              │
                              ▼
                          Format output
                              │
                              ▼
◄─────────────────────  Display results
Metrics:
   Duration: 1.2s
   ICMS: R$ 180
✅ Success
```

### CLI Output Example

```bash
$ forge_base execute IssueInvoiceUseCase \
    --input '{"order_value": 1000, "uf": "SP"}' \
    --verbose

╔═══════════════════════════════════════════════════╗
║  ForgeBase CLI - UseCase Execution                ║
╚═══════════════════════════════════════════════════╝

Starting IssueInvoiceUseCase...
Observability enabled
Tracing ID: exec-abc123

┌─────────────────────────────────────────────────┐
│ PHASE 1: Validation                             │
└─────────────────────────────────────────────────┘
  [DEBUG] Validating input DTO...
  [INFO]  Input valid ✅

┌─────────────────────────────────────────────────┐
│ PHASE 2: Business Logic                         │
└─────────────────────────────────────────────────┘
  [INFO]  Fetching ICMS rate for UF=SP...
  [INFO]  ICMS rate: 18%
  [INFO]  Calculating ICMS...
  [INFO]  ICMS: R$ 180.00 ✅

┌─────────────────────────────────────────────────┐
│ PHASE 3: Side Effects                           │
└─────────────────────────────────────────────────┘
  [INFO]  Generating NF-e XML...
  [INFO]  XML size: 2.5KB ✅
  [INFO]  Logging emission...
  [INFO]  Log saved ✅

┌─────────────────────────────────────────────────┐
│ RESULT                                          │
└─────────────────────────────────────────────────┘
  {
    "success": true,
    "invoice_id": "nfe-12345",
    "icms": 180.00,
    "xml_size_kb": 2.5,
    "duration_ms": 1247
  }

METRICS
  Duration: 1.247s
  Success: true
  ICMS calculated: R$ 180.00

✅ Execution completed successfully!
```

---

<a name="phase-5-feedback"></a>
## Phase 5: Feedback (Reflection)

### Two Types of Feedback

```
┌────────────────────────────────────────────────────┐
│ OPERATIONAL FEEDBACK                               │
│ (Technical metrics)                                │
├────────────────────────────────────────────────────┤
│                                                    │
│  Source: Logs, Metrics, Traces                     │
│                                                    │
│  Example:                                          │
│  - Duration: 1.2s (target: < 2s) ✅               │
│  - Error rate: 0.1% (target: 0%) ⚠️               │
│  - Throughput: 100 req/s                           │
│  - P95 latency: 1.8s                               │
│                                                    │
│  Action:                                           │
│  → Add retry logic                                 │
│  → Optimize ICMS calculation                       │
│                                                    │
└────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────┐
│ VALUE FEEDBACK                                     │
│ (Business validation)                              │
├────────────────────────────────────────────────────┤
│                                                    │
│  Source: Stakeholders, KPIs, Users                 │
│                                                    │
│  Example:                                          │
│  - KPI Target: 0% errors                           │
│  - KPI Actual: 0.1% errors ⚠️                      │
│  - User feedback: "Calculation takes too long"     │
│                                                    │
│  Action:                                           │
│  → Review calculation rules                        │
│  → Adjust ValueTrack in MDD                        │
│  → Add scenario in BDD                             │
│                                                    │
└────────────────────────────────────────────────────┘
```

### Complete Feedback Flow

```
Execution (CLI)
      ↓
┌─────────────────┐
│ Collect Metrics │
│  - Duration     │
│  - Errors       │
│  - Success rate │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Analyze KPIs   │
│  - Target met?  │
│  - Trends       │
│  - Anomalies    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Generate Report │
│  - Operational  │
│  - Business     │
│  - Recommendations │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Export Learning │
│  Data (JSONL)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  ForgeProcess   │
│  - Read feedback │
│  - Adjust MDD   │
│  - Refine BDD   │
└─────────────────┘
```

---

<a name="complete-example"></a>
## Complete Example: From Value to Feedback

### End-to-End Visualization

```
WEEK 1: MDD
───────────
forge.yaml created
   ValueTrack: "IssueInvoice"
   KPI: "0% errors in calculation"
   ↓
─────────────────────────────────────

WEEK 2: BDD
───────────
issue_invoice.feature created
   Scenario: Correct ICMS calculation
   Given order R$ 1000 in SP
   Then ICMS should be R$ 180
   ↓
─────────────────────────────────────

WEEK 3: TDD
───────────
test_issue_invoice.py created
   RED: Test fails
   GREEN: Code passes
   REFACTOR: Code improved
   ↓
─────────────────────────────────────

WEEK 4: CLI
───────────
Manual test via CLI
   $ forge_base execute IssueInvoice
   ✅ ICMS: R$ 180 (correct!)
   Duration: 1.2s
   ↓
─────────────────────────────────────

WEEKS 5-8: PRODUCTION
─────────────────────
System in production
   1000 invoices issued
   3 errors found (0.3%)
   ↓
─────────────────────────────────────

WEEK 9: FEEDBACK
────────────────
Feedback analysis
   KPI Target: 0% errors
   KPI Actual: 0.3% errors ⚠️

   Cause: Edge cases in
          tax substitution

   Recommendation:
   - Add rule in MDD
   - Add scenario in BDD
   - Implement with TDD
   ↓
─────────────────────────────────────

WEEK 10: ADJUSTMENT
───────────────────
Cycle restarts
   forge.yaml updated
   New feature added
   Tests expanded
   ↓
─────────────────────────────────────

RESULT: CONTINUOUS IMPROVEMENT
──────────────────────────────
✅ System learns from errors
✅ Documentation always up to date
✅ Quality continuously increases
```

### Visual Timeline

```
Time  │
═════════════════════════════════════════════════════
      │
W1-2  │ ███ MDD + BDD (Specification)
      │
W3    │     ███ TDD (Implementation)
      │
W4    │         ██ CLI (Validation)
      │
W5-8  │            ████████████ Production
      │
W9    │                        ███ Feedback
      │
W10+  │                           ████ Cycle 2
      │                               (MDD → BDD → ...)
      │
      └────────────────────────────────────────────>
```

---

## Checklist: How to Know If You Are Using ForgeProcess Correctly

### MDD
- [ ] Do you have a forge.yaml with defined ValueTracks?
- [ ] Does each ValueTrack have a measurable Value KPI?
- [ ] Are stakeholders identified?
- [ ] Can you explain WHY the system exists?

### BDD
- [ ] Does each ValueTrack have a .feature file?
- [ ] Do Scenarios use Given/When/Then?
- [ ] Are business rules documented?
- [ ] Can any stakeholder read and understand them?

### TDD
- [ ] Does each Scenario have automated tests?
- [ ] Do you write the test BEFORE the code?
- [ ] Is the Red-Green-Refactor cycle followed?
- [ ] Coverage > 90%?

### CLI
- [ ] Can UseCases be executed via CLI?
- [ ] Are logs and metrics collected?
- [ ] Can AI explore behaviors via CLI?
- [ ] Is debugging easy?

### Feedback
- [ ] Are operational metrics collected?
- [ ] Are Value KPIs measured regularly?
- [ ] Does feedback flow back to MDD and BDD?
- [ ] Does the system continuously improve?

---

## Next Steps

1. **Read the complete document**: [docs/FORGE_PROCESS.md](FORGE_PROCESS.md)
2. **See the technical integration**: [docs/adr/006-forgeprocess-integration.md](adr/006-forgeprocess-integration.md)
3. **Experiment**: Create your first forge.yaml
4. **Practice**: Write a .feature for a ValueTrack
5. **Implement**: Use TDD to develop
6. **Observe**: Execute via CLI and collect feedback

---

**Author**: ForgeBase Development Team
**Date**: 2025-11-04
**Version**: 1.0

> *"A diagram is worth a thousand words. A thousand executions are worth more than a diagram."*
