# ForgeProcess: Complete Cognitive Cycle

**The reasoning that transforms intent into execution and learning.**

---

## The Renaissance of Value-Driven Development

### From Time to Tokens: A Paradigm Shift

For years, software development was governed by methodologies that measured effort in **time** — hours, sprints, deliveries. **ForgeProcess** proposes a radical inversion: **measure value in tokens, not in time**.

```
Traditional:    "How many days will it take?"
                 ↓
ForgeProcess:   "How many value tokens did we deliver?"
```

#### What Are Value Tokens?

**Value Token** = A unit of meaningful behavior that delivers results to the customer

Examples:
- "We implemented 5 classes" → Technical effort
- "We reduced cart abandonment by 20%" → **Value Token**

- "We created 15 tests" → Activity
- "We ensured 0 errors in tax calculation" → **Value Token**

#### The Shift in Focus

| Traditional Metric | ForgeProcess |
|--------------------|--------------|
| Delivery speed | **Value direction** |
| "We delivered in 2 weeks" | "We increased conversion by 15%" |
| Sprint points | **Value tokens** |
| Features implemented | **Validated behaviors** |

> *"It doesn't matter how fast the team progresses if it's heading in the wrong direction."*

---

## Overview

**ForgeProcess** is the architectural reasoning system of the Forge Framework. It is not just a methodology, but a **cognitive cycle** that transforms:

```
Intent (Value) → Behavior → Proof → Execution → Learning → More Value
```

ForgeProcess operates in **5 integrated phases**, each representing a level of thought refinement:

```
┌─────────────────────────────────────────────────────┐
│ 1. MDD — Market Driven Development                  │
│    "WHY should it exist?"                           │
│    Value Intent                                     │
└────────────────┬────────────────────────────────────┘
                 │
                 │ Cognitive Translation
                 │ (Value → Behavior)
                 ▼
┌─────────────────────────────────────────────────────┐
│ 2. BDD — Behavior Driven Development                │
│    "WHAT to do?"                                    │
│    Verifiable Behavior                              │
└────────────────┬────────────────────────────────────┘
                 │
                 │ Technical Specification
                 ▼
┌─────────────────────────────────────────────────────┐
│ 3. TDD — Test Driven Development                    │
│    "HOW to do it? (with proof)"                     │
│    Validated Implementation                         │
└────────────────┬────────────────────────────────────┘
                 │
                 │ Executable Manifestation
                 ▼
┌─────────────────────────────────────────────────────┐
│ 4. CLI — Cognitive Interface                        │
│    "Execute and observe"                            │
│    Symbolic Environment                             │
└────────────────┬────────────────────────────────────┘
                 │
                 │ Evidence Collection
                 ▼
┌─────────────────────────────────────────────────────┐
│ 5. Feedback — Reflection                            │
│    "Learn and adjust"                               │
│    Reflexive Reasoning                              │
└────────────────┬────────────────────────────────────┘
                 │
                 │ Learning Loop
                 └─────────────────────┐
                                       │
                  ┌────────────────────┘
                  ▼
              Back to MDD
             (Cycle closes)
```

---

## The Five Phases of ForgeProcess

### 1. MDD — Market Driven Development

**"WHY should this system exist?"**

#### Purpose
Define the **market value** that the system delivers. This is the phase where **business strategy** transforms into **architectural intent**.

#### Main Artifacts
- **`forge.yaml`**: Declarative vision document
- **ValueTracks**: Flows that deliver direct value to the user (what the customer sees)
- **SupportTracks**: Flows that support value delivery (the invisible foundation)
- **Value KPIs**: Metrics that prove value delivery

#### ValueTracks vs SupportTracks: The Value Symbiosis

```
┌─────────────────────────────────────────────────────┐
│ VALUE TRACKS                                        │
│ "What the customer sees and experiences"            │
├─────────────────────────────────────────────────────┤
│ - Process an order in 1 click                       │
│ - Reduce cart abandonment by 20%                    │
│ - Issue invoices without errors                     │
│ - Real-time tracking                                │
│                                                     │
│ Measured by: Business impact (KPIs)                 │
└─────────────────────────────────────────────────────┘
                       ▲
                       │ supported by
                       │
┌─────────────────────────────────────────────────────┐
│ SUPPORT TRACKS                                      │
│ "What ensures reliability and quality"              │
├─────────────────────────────────────────────────────┤
│ - Automated BDD tests                               │
│ - CI/CD pipeline                                    │
│ - Monitoring and observability                      │
│ - Infrastructure and scalability                    │
│                                                     │
│ Measured by: Technical reliability (Metrics)        │
└─────────────────────────────────────────────────────┘
```

**Bidirectional Flow**:
- **Value → Support**: "We need 1-click checkout" generates the need for "Automated payment tests"
- **Support → Value**: "Robust CI/CD pipeline" enables "Fearless daily deployments"

**Complete Example**:

| Type | Track | Value Token | Measurement |
|------|-------|-------------|-------------|
| VALUE | "1-click checkout" | 20% reduction in abandonment | Conversion increased from 60% → 80% |
| SUPPORT | "Automated BDD tests" | 0 bugs in production | 100% scenarios passing |
| VALUE | "Automatic invoicing" | 0 tax errors | Fines avoided: $0 |
| SUPPORT | "CI/CD with tax validation" | Safe deployment | 95% of commits auto-validated |

> *"Every business behavior needs technical support — and every technical automation must justify its existence through the value it enables."*

#### Example: forge.yaml

```yaml
# forge.yaml
project:
  name: "OrderManagement"
  vision: "Enable merchants to manage orders quickly and securely"

value_proposition:
  - "Reduce order processing time by 50%"
  - "Eliminate manual errors in invoice issuance"
  - "Increase customer satisfaction with real-time tracking"

value_tracks:
  - name: "ProcessOrder"
    description: "Process a complete order from start to finish"
    value_metric: "Average processing time < 2 minutes"
    stakeholders:
      - "Merchant"
      - "End customer"

  - name: "IssueInvoice"
    description: "Issue invoices automatically"
    value_metric: "0 manual errors in tax calculation"
    stakeholders:
      - "Merchant"
      - "Accountant"

support_tracks:
  - name: "ManageInventory"
    description: "Control product inventory"
    supports: ["ProcessOrder"]

  - name: "CalculateTaxes"
    description: "Calculate taxes correctly"
    supports: ["IssueInvoice"]

kpis:
  - metric: "Order Processing Time"
    target: "< 2 minutes"
    current: "4.5 minutes"

  - metric: "Invoice Error Rate"
    target: "0%"
    current: "3.2%"
```

#### Questions MDD Answers
- What problem are we solving?
- Who are we solving it for?
- How do we measure if we are delivering value?
- What is the competitive advantage?

---

### Critical Transition: MDD → BDD

**The moment of cognitive translation: Value → Behavior**

This is the most important transition in ForgeProcess. Here, abstract value concepts transform into concrete, verifiable actions.

#### Mapping

| From MDD | To BDD |
|----------|--------|
| **Purpose**: "The system helps users process orders quickly" | **Scenario**: "Given a valid order, when I process it, then it should be completed in < 2 minutes" |
| **ValueTrack**: "IssueInvoice" | **Feature**: "Automatic invoice issuance with tax calculation" |
| **Value KPI**: "0 errors in calculation" | **Acceptance Criterion**: "All taxes must be calculated correctly" |

#### Translation Example

**MDD (Intent)**:
```yaml
value_tracks:
  - name: "CreateUser"
    description: "Enable fast and secure user registration"
    value_metric: "95% of registrations completed in < 30 seconds"
```

**BDD (Behavior)**:
```gherkin
Feature: Fast and secure user registration
  So that users can start using the system quickly
  As a visitor
  I want to register simply and securely

  Scenario: Successful registration
    Given I am on the registration page
    And I fill in the name "Alice Silva"
    And I fill in the email "alice@example.com"
    And I fill in a valid password
    When I click on "Create account"
    Then my account should be created in less than 30 seconds
    And I should receive a confirmation email
    And the system should validate that the email is unique
```

#### Why is this Transition Cognitive?

1. **Abstract → Concrete**: Value (abstract) becomes behavior (concrete)
2. **Intent → Action**: Purpose becomes an executable scenario
3. **Metric → Criterion**: KPI becomes acceptance criterion
4. **Strategy → Tactics**: Vision becomes specification

---

### 2. BDD — Behavior Driven Development

**"WHAT does the system do?"**

#### Purpose
Define **observable behaviors** of the system in natural language. Each behavior is a contract between stakeholders and developers.

#### Main Artifacts
- **Features**: `.feature` files in Gherkin
- **Scenarios**: Concrete use cases
- **Steps**: Given / When / Then
- **Business Rules**: Documented rules

#### Example: Feature File

```gherkin
# features/issue_invoice.feature
Feature: Invoice issuance
  So that merchants can bill their sales
  As a management system
  I should issue invoices automatically

  Background:
    Given the system is configured for NF-e issuance
    And the SEFAZ credentials are valid

  Scenario: Successful invoice issuance
    Given a valid order worth R$ 1000.00
    And the customer has CPF "123.456.789-00"
    And the product is taxable with 18% ICMS
    When I issue the invoice
    Then the system should calculate ICMS of R$ 180.00
    And the NF-e XML should be generated
    And the audit log should record the issuance
    And the invoice should be sent to SEFAZ
    And the customer should receive the DANFE by email

  Scenario: Issuance failure due to product without tax code
    Given an order with a product without an NCM code
    When I try to issue the invoice
    Then the system should reject with error "PRODUTO_SEM_NCM"
    And no invoice should be generated
    And the log should record the failed attempt

  Business Rules:
    - All products must have a valid NCM code
    - ICMS must be calculated according to the state tax table
    - Invoices must be numbered sequentially
    - SEFAZ failures must have automatic retry (3x)
```

#### How BDD Connects with ForgeBase

Each **Scenario** generates:
1. **UseCase** in ForgeBase
2. Automated **Acceptance Tests**
3. **Living Documentation** (specs are docs)

#### Tools
- Behave (Python)
- Cucumber
- SpecFlow

#### BDD as the Universal Language of Forge

**Why is BDD the natural language of ForgeProcess?**

```
Stakeholder (Business)  ──┐
                         │
Product Owner (Product) ──┼──> EVERYONE SPEAKS GHERKIN
                         │
Developer (Code)        ──┤
                         │
QA (Testing)            ──┘
```

**Before BDD** (everyone speaks a different language):
- Business: "We need to increase sales"
- Product: "Let's build a fast checkout"
- Dev: "I implemented a PaymentService with factory pattern"
- QA: "I tested 15 test cases from Jira"

**Problem**: No one can guarantee everyone is talking about the same thing!

**With BDD** (everyone speaks the same language):

```gherkin
FEATURE: 1-click checkout
  IN ORDER TO increase sales conversion        ← Business understands
  AS a returning buyer                          ← Product understands
  I WANT to complete a purchase with one click  ← Everyone understands

  SCENARIO: Fast purchase with saved card
    GIVEN I have a saved card                   ← Dev implements
    WHEN I click "Buy now"                      ← QA tests
    THEN I see "Purchase confirmed!"            ← Business validates
    AND I receive a confirmation email           ← Everyone verifies
```

**Solution**: A single specification that everyone understands, implements, and validates!

**Forge Standard: Tags in UPPERCASE (Portuguese)**

```gherkin
# ✅ CORRECT (Forge standard)
FUNCIONALIDADE: Emissão de nota fiscal
  CENÁRIO: Cálculo de ICMS
    DADO pedido de R$ 1000 em SP
    QUANDO emitir nota
    ENTÃO ICMS deve ser R$ 180

# ❌ Avoid (English or mixed)
Feature: Invoice issuance
  Scenario: ICMS calculation
    Given order of R$ 1000 in SP
    ...
```

**Why uppercase and Portuguese?**
1. **Reduces ambiguity**: DADO/QUANDO/ENTÃO are clearly structural tags
2. **Democratizes access**: Brazilian stakeholders understand without a language barrier
3. **Living documentation**: The code AND the documentation are the same artifact
4. **Traceability**: Every line of code traces back to a behavior

**Lifecycle of a Behavior**:

```
1. Stakeholder expresses value
   "I want to reduce cart abandonment"

2. PO writes in Gherkin
   FUNCIONALIDADE: 1-click checkout
   CENÁRIO: Fast purchase

3. Dev implements
   class QuickCheckoutUseCase(UseCaseBase):
       def execute(self, input):
           # Implementation based on the CENÁRIO

4. QA validates automatically
   pytest features/checkout.feature
   ✅ CENÁRIO: Fast purchase.....PASSED

5. Stakeholder confirms
   "Yes! Abandonment dropped 20%"

6. Everyone speaks the same language
   The behavior became code became test became value
```

> *"BDD is not just testing. It is the grammar that ForgeProcess adopts so that everyone — product, business, engineering, and QA — speaks the same language."*

---

### 3. TDD — Test Driven Development

**"HOW to implement? (with proof)"**

#### Purpose
Transform BDD behaviors into **tested code**. Every feature is born with proof that it works.

#### TDD Cycle (Red-Green-Refactor)

```
1. RED: Write a failing test
   ↓
2. GREEN: Implement minimum code that passes
   ↓
3. REFACTOR: Improve code while keeping tests green
   ↓
   Repeat
```

#### Example: From BDD to TDD

**BDD Scenario**:
```gherkin
Scenario: Successful invoice issuance
  Given a valid order worth R$ 1000.00
  When I issue the invoice
  Then ICMS should be R$ 180.00
```

**TDD Test (Red)**:
```python
# tests/unit/test_issue_invoice_usecase.py
import pytest
from forge_base.application.issue_invoice_usecase import IssueInvoiceUseCase

def test_should_calculate_icms_correctly():
    # Arrange
    usecase = IssueInvoiceUseCase()
    order = Order(value=1000.00, uf="SP")  # ICMS SP = 18%

    # Act
    invoice = usecase.execute(IssueInvoiceInput(order=order))

    # Assert
    assert invoice.icms == 180.00  # FAILS - code doesn't exist yet
```

**TDD Implementation (Green)**:
```python
# src/forge_base/application/issue_invoice_usecase.py
from forge_base.application.usecase_base import UseCaseBase

class IssueInvoiceUseCase(UseCaseBase[IssueInvoiceInput, IssueInvoiceOutput]):
    """Issue invoice with automatic tax calculation."""

    def execute(self, input_dto: IssueInvoiceInput) -> IssueInvoiceOutput:
        # Validate input
        input_dto.validate()

        # Calculate ICMS
        icms_rate = self._get_icms_rate(input_dto.order.uf)
        icms_value = input_dto.order.value * icms_rate

        # Generate XML
        xml = self._generate_nfe_xml(input_dto.order, icms_value)

        # Record log
        self._log_emission(input_dto.order, xml)

        return IssueInvoiceOutput(
            xml=xml,
            icms=icms_value,
            success=True
        )

    def _get_icms_rate(self, uf: str) -> float:
        """Get ICMS rate by state."""
        icms_table = {"SP": 0.18, "RJ": 0.20, "MG": 0.18}
        return icms_table.get(uf, 0.17)  # Default 17%
```

**Test passes**

#### Test Types in ForgeBase

1. **Unit Tests**: Test UseCases in isolation
2. **Integration Tests**: Test UseCases with real Repositories
3. **Property-Based Tests**: Test general properties (Hypothesis)
4. **Contract Tests**: Validate interfaces (Ports)

---

### 4. CLI — Cognitive Interface

**"Execute and observe"**

#### Purpose
Provide a **symbolic testing environment** where UseCases can be executed, observed, and validated before a graphical interface.

The CLI is not just a command-line tool, but a **cognitive space** where:
- Humans can test manually
- AI can explore behaviors
- Logs and metrics are collected
- Debugging is facilitated

#### Example: ForgeBase CLI

```bash
# Execute UseCase via CLI
forge_base execute IssueInvoiceUseCase \
  --input '{"order_id": "12345", "value": 1000.00, "uf": "SP"}' \
  --output invoice.json \
  --verbose

# Output:
# Starting IssueInvoiceUseCase...
# Metrics enabled: true
# Tracing enabled: true
#
# [DEBUG] Validating input...
# [INFO] Fetching order 12345...
# [INFO] Calculating ICMS for UF=SP (18%)...
# [INFO] ICMS calculated: R$ 180.00
# [INFO] Generating NF-e XML...
# [SUCCESS] Invoice issued successfully!
#
# Metrics:
#   - Duration: 1.2s
#   - ICMS: R$ 180.00
#   - XML size: 2.5KB
#
# Output saved to invoice.json
```

#### CLI Capabilities

1. **Manual Execution**: Test UseCases without GUI
2. **Simulation**: Run scenarios with fake data
3. **Observation**: View logs, metrics, traces in real time
4. **Debugging**: Inspect state and flow
5. **Automation**: Scripts and CI/CD
6. **Exploration**: AI can use CLI to learn

#### CLI as a Bridge Between Humans and AI

```python
# AI exploring via CLI
from forge_base.dev.api import ComponentDiscovery, TestRunner

# 1. AI discovers components
discovery = ComponentDiscovery()
components = discovery.scan_project()
print(f"Found {len(components.usecases)} UseCases")

# 2. AI executes each UseCase via CLI
for usecase in components.usecases:
    result = subprocess.run([
        "forge_base", "execute", usecase.name,
        "--input", "sample_input.json"
    ])

    # 3. AI analyzes the result
    if result.returncode == 0:
        print(f"✅ {usecase.name} works!")
    else:
        print(f"❌ {usecase.name} failed!")
```

---

### 5. Feedback — Reflection

**"Learn and adjust"**

#### Purpose
Collect execution data and use it to **improve the system's reasoning**. Feedback closes the cognitive cycle.

#### Two Types of Feedback

##### 1. Operational Feedback

**Source**: Metrics, logs, exceptions, performance
**Function**: Improve technical performance

```python
# Automatic metrics collection
@track_metrics
class IssueInvoiceUseCase(UseCaseBase):
    def execute(self, input_dto):
        # Metrics collected automatically:
        # - Execution time
        # - Error rate
        # - Throughput
        # - Dependency latency
        ...

# Metrics analysis
metrics = MetricsCollector.get_metrics("IssueInvoiceUseCase")
print(f"Avg duration: {metrics.avg_duration}ms")
print(f"Error rate: {metrics.error_rate}%")
print(f"P95 latency: {metrics.p95_latency}ms")

# AI analyzes and suggests improvements
if metrics.error_rate > 0.05:
    print("⚠️ High error rate detected!")
    print("💡 Suggestion: Add retry logic for SEFAZ calls")
```

##### 2. Value Feedback

**Source**: Stakeholders, users, KPIs
**Function**: Adjust purpose and realign value

```python
# Value KPI analysis
value_tracker = ValueKPITracker()

# MDD KPI: "0 errors in tax calculation"
kpi_result = value_tracker.measure_kpi(
    kpi="Invoice Error Rate",
    usecase="IssueInvoiceUseCase",
    period="last_30_days"
)

print(f"Target: 0%")
print(f"Current: {kpi_result.current_value}%")

if kpi_result.current_value > 0:
    print("❌ KPI not met!")

    # Feedback to MDD: review ValueTrack
    feedback = FeedbackReport(
        kpi="Invoice Error Rate",
        target=0.0,
        actual=kpi_result.current_value,
        recommendation="Review ICMS calculation rules for edge cases"
    )

    # Export to ForgeProcess
    feedback_manager.export_to_forgeprocess(feedback)
```

#### Complete Feedback Loop

```python
# src/forge_base/observability/feedback_manager.py
class FeedbackManager:
    """Manages feedback loops between ForgeBase and ForgeProcess."""

    def collect_comprehensive_feedback(
        self,
        usecase_name: str,
        time_window: str = "last_7_days"
    ) -> FeedbackReport:
        """Collects comprehensive feedback from a UseCase."""

        # 1. Operational metrics
        metrics = self.metrics_collector.get_metrics(usecase_name, time_window)

        # 2. Error logs
        errors = self.log_service.query_errors(usecase_name, time_window)

        # 3. Value KPIs
        kpis = self.value_tracker.measure_all_kpis(usecase_name, time_window)

        # 4. Intent tracking (coherence)
        coherence = self.intent_tracker.measure_coherence(usecase_name, time_window)

        # 5. AI analysis
        insights = self.ai_analyzer.analyze(metrics, errors, kpis, coherence)

        return FeedbackReport(
            usecase=usecase_name,
            operational_metrics=metrics,
            errors=errors,
            value_kpis=kpis,
            coherence=coherence,
            ai_insights=insights,
            recommendations=self._generate_recommendations(insights)
        )

    def export_to_forgeprocess(self, report: FeedbackReport):
        """Exports feedback for ForgeProcess to learn from."""
        # Save in structured format
        learning_data = {
            "usecase": report.usecase,
            "timestamp": datetime.now().isoformat(),
            "metrics": report.operational_metrics.to_dict(),
            "kpis": [kpi.to_dict() for kpi in report.value_kpis],
            "recommendations": report.recommendations
        }

        # Export to ForgeProcess
        with open(f"/var/learning/{report.usecase}_feedback.jsonl", "a") as f:
            f.write(json.dumps(learning_data) + "\n")

        # ForgeProcess can read and adjust forge.yaml or .feature files
```

---

## The Complete Cycle in Practice

### Real Example: ValueTrack "IssueInvoice"

#### Phase 1: MDD

```yaml
# forge.yaml
value_tracks:
  - name: "IssueInvoice"
    description: "Issue invoices automatically"
    value_metric: "0 errors in tax calculation"
    stakeholders: ["Merchant", "Accountant"]
```

#### Phase 2: BDD

```gherkin
# features/issue_invoice.feature
Feature: Invoice issuance
  Scenario: Correct ICMS calculation
    Given an order of R$ 1000 in SP
    When I issue the invoice
    Then ICMS should be R$ 180
```

#### Phase 3: TDD

```python
# tests/test_issue_invoice.py
def test_icms_calculation():
    usecase = IssueInvoiceUseCase()
    result = usecase.execute(IssueInvoiceInput(order_value=1000, uf="SP"))
    assert result.icms == 180.00
```

#### Phase 4: CLI

```bash
forge_base execute IssueInvoiceUseCase \
  --input '{"order_value": 1000, "uf": "SP"}' \
  --verbose

# ICMS: R$ 180.00
# XML generated
# Duration: 1.2s
```

#### Phase 5: Feedback

```python
# Analysis after 30 days
feedback = feedback_manager.collect_comprehensive_feedback("IssueInvoiceUseCase")

# KPI: 0 errors → ACTUAL: 0.1% errors
# Recommendation: Add validation for tax substitution edge cases

# Feedback returns to MDD: Adjust ValueTrack
# Feedback returns to BDD: Add scenarios for tax substitution
```

---

## Benefits of the Cognitive Cycle

### 1. Complete Traceability

```
Value (MDD) → Behavior (BDD) → Code (TDD) → Execution (CLI) → Learning (Feedback)
```

All code can be traced back to the original value intent.

### 2. Living Documentation

- **forge.yaml** documents the why
- **.feature** documents the what
- **Tests** document the how
- **Logs** document what happened
- **Feedback** documents the learning

### 3. Value-Guided Evolution

The system does not evolve randomly, but guided by:
- Value KPIs (are we delivering value?)
- Operational Metrics (are we running well?)
- Coherence Tracking (are we fulfilling intents?)

### 4. Cognitive Environment for AI

AI can:
- Read **forge.yaml** and understand purpose
- Execute **.features** and validate behaviors
- Analyze **metrics** and suggest improvements
- Use **CLI** to explore and test
- Generate **feedback** for self-improvement

---

## Next Steps

### For Developers

1. Read your project's **forge.yaml**
2. Understand the **ValueTracks** (what delivers value?)
3. Write **.features** for each ValueTrack
4. Implement with **TDD** (tests first)
5. Test via **CLI** (observe and validate)
6. Analyze **feedback** (learn and improve)

### For AI Agents

1. Parse **forge.yaml** → Understand purpose
2. Parse **.features** → Understand behaviors
3. Execute via **CLI** → Validate functionality
4. Collect **metrics** → Analyze performance
5. Generate **feedback** → Suggest improvements

### For Product Owners

1. Define clear **Value KPIs**
2. Track value metrics
3. Use feedback to adjust roadmap
4. Validate that features deliver value

---

## Related Documents

- **ADR-006**: ForgeProcess Integration (technical details)
- **AGENT_ECOSYSTEM.md**: How AI uses ForgeProcess
- **AI_AGENT_QUICK_START.md**: APIs for agents
- **forgebase_PRD.md**: Product vision

---

## The Forge Philosophy: Value Tokens, Not Sprint Days

### What Are We Really Measuring?

ForgeProcess proposes something deeper than speed: **clarity, coherence, and confidence**.

```
Traditional Methodology           ForgeProcess
═══════════════════════           ════════════

"We delivered 20 story points"    "We reduced abandonment by 20%"
"We completed 15 tasks"           "We ensured 0 tax bugs"
"Sprint completed in 2 weeks"     "Customer saved $50k/month"
"5 features implemented"          "5 validated behaviors"

Measures: ACTIVITY                Measures: IMPACT
```

### Why "Value Tokens"?

**Value Token** = The smallest unit of behavior that delivers measurable results

Each token is:
1. **Traceable**: From forge.yaml to code
2. **Verifiable**: Automated BDD scenarios
3. **Measurable**: Clear impact KPIs
4. **Valuable**: Customer perceives the difference

### The Verifiable Value Chain

```
MDD (Value Intent)
    ↓
BDD (Verifiable Behavior)
    ↓
TDD (Automated Proof)
    ↓
CLI (Real-Time Observation)
    ↓
Feedback (Impact Measurement)
    ↓
More Value (Continuous Cycle)
```

Every link in this chain is **verifiable**:
- Value defined? (forge.yaml)
- Behavior specified? (.feature)
- Code tested? (pytest)
- Works in production? (CLI + metrics)
- KPI met? (feedback)

### The Value <-> Support Symbiosis

ForgeProcess establishes a contract:

**VALUE TRACKS** deliver impact
**SUPPORT TRACKS** ensure reliability

```
       VALUE                        SUPPORT
   ┌──────────┐                ┌──────────┐
   │ 1-click  │                │ Tests    │
   │ Checkout │ ←──────────→  │ BDD auto │
   │          │   support      │          │
   │ -20%     │                │ 100%     │
   │ abandon  │                │ coverage │
   └──────────┘                └──────────┘
```

Without VALUE TRACKS, the system has no purpose.
Without SUPPORT TRACKS, value is unsustainable.

### The Renaissance

**In a world saturated with fast deliveries and shallow results**, ForgeProcess proposes:

- **Cognitive cycle** instead of mechanical workflow
- **Value direction** instead of blind speed
- **Universal language** (BDD) instead of technical silos
- **Value tokens** instead of story points
- **Validated behaviors** instead of "done" features
- **Complete traceability** from the why to the code

### Code Reconciling with Purpose

```
Traditional:                    ForgeProcess:
"Feature done!"                "Value delivered!"
    ↓                              ↓
But does it work?              Yes, it's tested.
    ↓                              ↓
But does it deliver value?     Yes, KPI shows it.
    ↓                              ↓
How do we know?                Behavior validated.
    ↓                              ↓
"We think so"                  "We have evidence"
```

---

## Quotes

> *"The ForgeBase code is the body of a mind that thinks in software."*

> *"ForgeProcess is the cycle in which thought transforms into behavior, behavior into proof, and proof into learning."*

> *"MDD → BDD: The moment when strategy becomes function."*

> *"It doesn't matter how fast the team progresses if it's heading in the wrong direction."*

> *"Every business behavior needs technical support — and every technical automation must justify its existence through the value it enables."*

> *"BDD is the grammar that everyone — product, business, engineering, and QA — uses to speak the same language."*

> *"Progress is measured in value tokens, not sprint days."*

> *"It is code reconciling with purpose."*

---

**Author**: ForgeBase Development Team
**Version**: 1.1
**Date**: 2025-11-04
**Updated**: 2025-11-04 - Added Value Tokens and ValueTracks vs SupportTracks concepts
