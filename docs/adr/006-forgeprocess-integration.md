# ADR-006: ForgeProcess Integration

## Status

**Aceita** (2025-11-03)

## Context

ForgeBase é o **núcleo de execução** do Forge Framework, mas não existe isoladamente. Ele é a **manifestação técnica** das intenções capturadas pelo ForgeProcess:

- **ForgeProcess**: Define **o quê** fazer (intent, YAML specs, processos)
- **ForgeBase**: Implementa **como** fazer (code, execution, infrastructure)

Para que o Forge Framework seja verdadeiramente **cognitivo**, precisa haver um **loop de feedback** entre intenção (ForgeProcess) e execução (ForgeBase):

```
┌──────────────────────────────────────────────────┐
│                                                  │
│  ForgeProcess (Intent Layer)                    │
│  - Define YAML specs                            │
│  - Captura intenções                            │
│  - Orquestra processos                          │
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
│  - Executa UseCases                             │
│  - Valida regras de negócio                     │
│  - Coleta métricas                              │
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
│  - Analisa coerência                            │
│  - Ajusta processos                             │
│  - Melhora especificações                       │
│                                                  │
└──────────────────────────────────────────────────┘
```

### Desafios

1. **Drift Detection**: Como detectar quando código não reflete mais a spec YAML?
2. **Bidirectional Sync**: Como manter YAML e código sincronizados?
3. **Coherence Validation**: Como medir se execução cumpriu a intenção?
4. **Learning Loop**: Como feedback de execução melhora especificações?
5. **Autonomia**: Como evitar que ForgeBase dependa de ForgeProcess em runtime?

### Forças em Jogo

**Necessidades:**
- Sincronização automática YAML ↔ Code
- Validação de coerência cognitiva
- Feedback loop para aprendizado
- Geração de código a partir de specs
- Detecção de divergências

**Riscos:**
- Acoplamento excessivo
- Overhead de sincronização
- Complexidade de manutenção
- Conflitos de merge (YAML vs Code)

## Decision

**Adotamos integração bidirecional com dois componentes principais: YAMLSync e IntentTracker.**

### 1. YAMLSync: Sincronização YAML ↔ Code

**Propósito**: Manter especificações YAML e código Python sincronizados.

#### YAML Schema para UseCases

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

#### Funcionalidades do YAMLSync

**1. Parse YAML → Validação**
```python
sync = YAMLSync()
spec = sync.parse_yaml("specs/create_user.yaml")
# Valida schema version, required fields, etc.
```

**2. Generate Code from YAML**
```python
code = sync.generate_code(spec)
# Gera:
# - Input DTO (CreateUserInput)
# - Output DTO (CreateUserOutput)
# - UseCase skeleton (CreateUserUseCase)
# - Docstrings com business rules
```

**Código gerado:**
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
# Reverse engineering: Código → YAML
```

#### Workflow de Desenvolvimento

**Opção A: YAML-First (Recomendado)**
```bash
# 1. Criar spec YAML
vim specs/create_user.yaml

# 2. Gerar código skeleton
forgebase generate usecase specs/create_user.yaml

# 3. Implementar lógica
vim src/application/create_user_usecase.py

# 4. Validar consistência
forgebase validate usecase CreateUserUseCase --spec specs/create_user.yaml
```

**Opção B: Code-First**
```bash
# 1. Implementar UseCase
vim src/application/create_user_usecase.py

# 2. Exportar para YAML
forgebase export usecase CreateUserUseCase --output specs/create_user.yaml

# 3. Refinar YAML no ForgeProcess
```

#### Integração com CI/CD

```yaml
# .github/workflows/validate.yml
- name: Validate YAML ↔ Code Sync
  run: |
    forgebase validate all-usecases --fail-on-drift
    # Falha se qualquer UseCase tem drift
```

### 2. IntentTracker: Coerência Cognitiva

**Propósito**: Validar que execução cumpre a intenção original.

#### Fluxo de Intent Tracking

**1. Capture Intent (ForgeProcess)**
```python
# Antes de executar
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
# Execução normal
result = usecase.execute(CreateUserInput(
    name="Alice",
    email="alice@example.com"
))
```

**3. Record Execution**
```python
# Após execução
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
# Análise de coerência
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
# Exportar dados para ML analysis
learning_data = intent_tracker.export_learning_data()

# Formato:
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

# Salvar para análise
with open("/var/learning/coherence_data.jsonl", "w") as f:
    for record in learning_data:
        f.write(json.dumps(record) + "\n")
```

### 3. Feedback Manager

**Propósito**: Orquestrar feedback de ForgeBase → ForgeProcess.

```python
# src/forgebase/observability/feedback_manager.py
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

### 4. Autonomia: Runtime Independence

**Princípio Crítico**: ForgeBase **não depende** de ForgeProcess em runtime.

```python
# ✅ ForgeBase funciona standalone
core = ForgeBaseCore()
usecase = core.get_usecase(CreateUserUseCase)
result = usecase.execute(input_dto)
# Sem ForgeProcess, sem YAML, funciona perfeitamente

# ✅ Com ForgeProcess, adiciona feedback
intent_id = intent_tracker.capture_intent(...)  # Opcional
result = usecase.execute(input_dto)
intent_tracker.record_execution(intent_id, ...)  # Opcional
```

**Autonomia garantida por:**
- YAMLSync é **build-time tool**, não runtime dependency
- IntentTracker é **opcional** (pode ser desabilitado)
- ForgeBase pode ser distribuído sem ForgeProcess
- YAML specs são documentation, não requirements

## Consequences

### Positivas

✅ **Sincronização Automática**
```bash
# Gerar código
forgebase generate usecase specs/create_user.yaml

# Validar consistência
forgebase validate usecase CreateUserUseCase
```

✅ **Coerência Validada Quantitativamente**
```python
report = intent_tracker.validate_coherence(intent_id)
assert report.similarity_score >= 0.80
```

✅ **Learning Loop**
```python
# Feedback automático para ForgeProcess
learning_data = intent_tracker.export_learning_data()
# ForgeProcess usa para melhorar specs
```

✅ **Documentation Viva**
```yaml
# YAML serve como documentação sempre atualizada
# Drift detection garante que código reflete spec
```

✅ **Desenvolvimento Guiado por Intent**
```bash
# 1. Spec define intenção (ForgeProcess)
# 2. Código implementa (ForgeBase)
# 3. Testes validam coerência
# 4. Feedback melhora spec
# 5. Repeat
```

### Negativas

⚠️ **Overhead de Sincronização**
- Manter YAML e código sincronizados requer disciplina
- Drift pode ocorrer se validação não estiver em CI

**Mitigation**: Validação automática em CI/CD

⚠️ **Complexidade de Tooling**
- YAMLSync e IntentTracker adicionam complexidade
- Curva de aprendizado

**Mitigation**: Docs claras, exemplos, defaults sensatos

⚠️ **Storage de Learning Data**
- Learning data pode crescer
- Precisa de storage e processamento

**Mitigation**: Retention policies, aggregation

⚠️ **Latência de Tracking**
- Intent tracking adiciona ~1-5ms por execução

**Mitigation**: Opcional, pode ser desabilitado em prod

### Mitigações Implementadas

1. **Autonomia Runtime**
   - ForgeBase funciona sem ForgeProcess
   - Intent tracking é opcional
   - Zero dependências em runtime

2. **Tooling Ergonômico**
   - CLI commands: `generate`, `validate`, `export`
   - IDE integration (futuro)
   - Auto-completion

3. **Defaults Sensatos**
   - Intent tracking desabilitado por default em prod
   - Sampling configurável
   - Performance overhead mínimo

## Alternatives Considered

### 1. Acoplamento Forte (Runtime Dependency)

```python
# ForgeBase depende de ForgeProcess em runtime
class CreateUserUseCase:
    def execute(self, input_dto):
        spec = ForgeProcess.get_spec("CreateUser")  # Runtime call
        ...
```

**Rejeitado porque:**
- Violação de autonomia
- ForgeBase não pode funcionar standalone
- Performance overhead
- Acoplamento desnecessário

### 2. Code-Only (Sem YAML)

**Rejeitado porque:**
- Perde especificação declarativa
- Sem feedback loop para ForgeProcess
- Código é source of truth (difícil para não-devs)

### 3. YAML-Only (Generated Code Never Edited)

**Rejeitado porque:**
- Código gerado é sempre limited
- Desenvolvedores precisam de flexibilidade
- Complexidade move para YAML (pior)

### 4. No Coherence Validation

**Rejeitado porque:**
- Miss oportunidade de learning
- Sem feedback quantitativo
- "Funciona" ≠ "Funciona como pretendido"

## Implementation Guidelines

### Para Desenvolvedores

**Workflow recomendado:**

1. **Definir Spec YAML** (com ForgeProcess)
   ```yaml
   # specs/my_usecase.yaml
   usecase:
     name: MyUseCase
     ...
   ```

2. **Gerar Skeleton**
   ```bash
   forgebase generate usecase specs/my_usecase.yaml
   ```

3. **Implementar Lógica**
   ```python
   # Editar código gerado
   class MyUseCaseUseCase(UseCaseBase):
       def execute(self, input_dto):
           # Implementação real
           ...
   ```

4. **Validar Consistência**
   ```bash
   forgebase validate usecase MyUseCase --spec specs/my_usecase.yaml
   ```

5. **Testes com Intent Tracking**
   ```python
   def test_my_usecase():
       intent_id = tracker.capture_intent(...)
       result = usecase.execute(input_dto)
       tracker.record_execution(intent_id, ...)

       report = tracker.validate_coherence(intent_id)
       assert report.coherence_level in [CoherenceLevel.PERFECT, CoherenceLevel.HIGH]
   ```

### Para Operadores

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
- ForgeProcess documentation
- YAML specification: https://yaml.org/spec/

## Related ADRs

- [ADR-001: Clean Architecture Choice](001-clean-architecture-choice.md)
- [ADR-003: Observability First](003-observability-first.md)
- [ADR-004: Cognitive Testing](004-cognitive-testing.md)

---

**Author:** ForgeBase Development Team
**Date:** 2025-11-03
**Version:** 1.0
