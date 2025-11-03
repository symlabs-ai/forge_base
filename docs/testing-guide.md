# ForgeBase Testing Guide

> "Testes não apenas validam comportamento — validam intenção."

Este guia ensina como escrever testes efetivos no ForgeBase, incluindo testes unitários tradicionais e **testes cognitivos** que validam coerência entre intenção e execução.

---

## 📚 Filosofia de Testes no ForgeBase

ForgeBase adota uma filosofia de testes em **três níveis**:

1. **Unit Tests** — Validam comportamento de componentes isolados
2. **Integration Tests** — Validam interação entre componentes
3. **Cognitive Tests** — Validam coerência entre intenção e execução

```
┌────────────────────────────────────────────┐
│          Cognitive Tests                   │  ← Valida INTENÇÃO
│  "O código faz o que PRETENDÍAMOS?"       │
└─────────────┬──────────────────────────────┘
              │
┌─────────────┴──────────────────────────────┐
│        Integration Tests                   │  ← Valida INTEGRAÇÃO
│  "Os componentes funcionam juntos?"        │
└─────────────┬──────────────────────────────┘
              │
┌─────────────┴──────────────────────────────┐
│           Unit Tests                       │  ← Valida COMPORTAMENTO
│  "Este componente funciona isoladamente?"  │
└────────────────────────────────────────────┘
```

---

## 🧪 1. Unit Tests (Testes Unitários)

### Estrutura Básica

```python
import unittest
from forgebase.domain import EntityBase, ValidationError


class TestUser(unittest.TestCase):
    """Unit tests for User entity."""

    def test_creates_user_with_valid_data(self):
        """Test user creation with valid inputs."""
        user = User(name="Alice", email="alice@example.com")

        self.assertEqual(user.name, "Alice")
        self.assertEqual(user.email, "alice@example.com")
        self.assertTrue(user.is_active)

    def test_rejects_empty_name(self):
        """Test that empty name raises ValidationError."""
        with self.assertRaises(ValidationError) as ctx:
            User(name="", email="alice@example.com")

        self.assertIn("name cannot be empty", str(ctx.exception).lower())
```

### O Que Testar?

#### Domain Layer

**Entities:**
- ✅ Validação de invariantes
- ✅ Métodos de negócio
- ✅ Igualdade baseada em ID
- ✅ State transitions

```python
class TestOrder(unittest.TestCase):
    def test_validates_positive_total(self):
        """Test that negative total is rejected."""
        with self.assertRaises(ValidationError):
            Order(customer_id="123", items=[], total=-10)

    def test_mark_as_paid_changes_status(self):
        """Test status transition to paid."""
        order = Order(customer_id="123", items=[...], total=50)
        order.mark_as_paid()

        self.assertEqual(order.status, "paid")
        self.assertIsNotNone(order.paid_at)

    def test_cannot_modify_paid_order(self):
        """Test business rule: paid orders are immutable."""
        order = Order(customer_id="123", items=[...], total=50)
        order.mark_as_paid()

        with self.assertRaises(BusinessRuleViolation):
            order.add_item({"name": "Item"}, 10)
```

**ValueObjects:**
- ✅ Imutabilidade
- ✅ Igualdade estrutural
- ✅ Validação de formato
- ✅ Operações (se aplicável)

```python
class TestEmail(unittest.TestCase):
    def test_validates_format(self):
        """Test email format validation."""
        with self.assertRaises(ValidationError):
            Email("invalid-email")

        # Valid
        email = Email("alice@example.com")
        self.assertEqual(str(email), "alice@example.com")

    def test_immutability(self):
        """Test that email is immutable."""
        email = Email("alice@example.com")

        with self.assertRaises(AttributeError):
            email.address = "bob@example.com"

    def test_equality(self):
        """Test structural equality."""
        email1 = Email("alice@example.com")
        email2 = Email("alice@example.com")

        self.assertEqual(email1, email2)
        self.assertEqual(hash(email1), hash(email2))
```

#### Application Layer

**UseCases:**
- ✅ Validação de input DTOs
- ✅ Orquestração correta
- ✅ Output DTOs corretos
- ✅ Error handling

```python
class TestCreateUserUseCase(unittest.TestCase):
    def setUp(self):
        self.fake_repo = FakeRepository()
        self.usecase = CreateUserUseCase(user_repository=self.fake_repo)

    def test_creates_user(self):
        """Test successful user creation."""
        output = self.usecase.execute(CreateUserInput(
            name="Alice",
            email="alice@example.com"
        ))

        self.assertIsNotNone(output.user_id)
        self.assertEqual(output.name, "Alice")

        # Verify persistence
        self.assertEqual(self.fake_repo.count(), 1)

    def test_rejects_duplicate_email(self):
        """Test business rule: email must be unique."""
        # Create first user
        self.usecase.execute(CreateUserInput(
            name="Alice",
            email="alice@example.com"
        ))

        # Try duplicate
        with self.assertRaises(BusinessRuleViolation) as ctx:
            self.usecase.execute(CreateUserInput(
                name="Bob",
                email="alice@example.com"
            ))

        self.assertIn("already exists", str(ctx.exception))
```

#### Infrastructure Layer

**Repositories:**
- ✅ CRUD operations
- ✅ Query methods
- ✅ Error handling

```python
class TestJSONRepository(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.file_path = os.path.join(self.temp_dir, "data.json")
        self.repo = JSONRepository(
            file_path=self.file_path,
            entity_type=User
        )

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_save_and_find(self):
        """Test save and retrieval."""
        user = User(name="Alice", email="alice@example.com")
        self.repo.save(user)

        found = self.repo.find_by_id(user.id)

        self.assertIsNotNone(found)
        self.assertEqual(found.id, user.id)
        self.assertEqual(found.name, "Alice")

    def test_persistence_across_instances(self):
        """Test data persists across repository instances."""
        user = User(name="Alice", email="alice@example.com")
        self.repo.save(user)

        # Create new repo instance
        new_repo = JSONRepository(
            file_path=self.file_path,
            entity_type=User
        )

        found = new_repo.find_by_id(user.id)
        self.assertIsNotNone(found)
```

### Padrões de Teste

#### Arrange-Act-Assert (AAA)

```python
def test_example(self):
    """Test following AAA pattern."""
    # Arrange: Setup
    user = User(name="Alice", email="alice@example.com")
    order = Order(customer_id=user.id, items=[], total=50)

    # Act: Execute
    order.mark_as_paid()

    # Assert: Verify
    self.assertEqual(order.status, "paid")
    self.assertIsNotNone(order.paid_at)
```

#### Given-When-Then (BDD Style)

```python
def test_example_bdd_style(self):
    """
    Given a pending order
    When marking as paid
    Then status should be 'paid' and paid_at should be set
    """
    # Given
    order = Order(customer_id="123", items=[], total=50, status="pending")

    # When
    order.mark_as_paid()

    # Then
    self.assertEqual(order.status, "paid")
    self.assertIsNotNone(order.paid_at)
```

---

## 🔗 2. Integration Tests

Integration tests validam a interação entre múltiplos componentes.

### Exemplo: UseCase + Repository

```python
class TestCreateUserIntegration(unittest.TestCase):
    """Integration tests for CreateUser flow."""

    def setUp(self):
        # Real components (not fakes)
        self.temp_dir = tempfile.mkdtemp()
        self.repo = JSONRepository(
            file_path=os.path.join(self.temp_dir, "users.json"),
            entity_type=User
        )
        self.logger = LogService(name="test")
        self.metrics = TrackMetrics()

        self.usecase = CreateUserUseCase(
            user_repository=self.repo,
            logger=self.logger,
            metrics=self.metrics
        )

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_complete_flow(self):
        """Test complete user creation flow."""
        # Execute
        output = self.usecase.execute(CreateUserInput(
            name="Alice",
            email="alice@example.com"
        ))

        # Verify all layers
        # 1. Output DTO correct
        self.assertIsNotNone(output.user_id)

        # 2. Persisted to repository
        user = self.repo.find_by_id(output.user_id)
        self.assertIsNotNone(user)

        # 3. Metrics collected
        report = self.metrics.report()
        self.assertIn('create_user', str(report))

        # 4. Logs generated
        # (Can verify if logger stores logs)
```

### Exemplo: YAML Sync Integration

```python
class TestYAMLSyncIntegration(unittest.TestCase):
    """Integration tests for YAML synchronization."""

    def test_parse_generate_validate_cycle(self):
        """Test complete YAML ↔ Code cycle."""
        sync = YAMLSync()

        # 1. Parse YAML
        spec = sync.parse_yaml("specs/test_usecase.yaml")

        # 2. Generate code
        code = sync.generate_code(spec)

        # 3. Write to temp file and import
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_path = f.name

        # 4. Import generated module
        spec_module = importlib.import_module(...)

        # 5. Validate no drift
        drift = sync.detect_drift(spec_module.GeneratedUseCase, spec)
        self.assertEqual(len(drift), 0)
```

---

## 🧠 3. Cognitive Tests

**Testes cognitivos** validam que a execução cumpre a intenção original. Usam `ForgeTestCase`.

### ForgeTestCase: Assertions Cognitivas

```python
from forgebase.testing import ForgeTestCase
from forgebase.testing.fakes import FakeRepository, FakeLogger, FakeMetricsCollector


class TestCreateUserCognitive(ForgeTestCase):
    """Cognitive tests for CreateUser UseCase."""

    def setUp(self):
        # Fakes for fast, isolated tests
        self.fake_repo = FakeRepository()
        self.fake_logger = FakeLogger()
        self.fake_metrics = FakeMetricsCollector()

        self.usecase = CreateUserUseCase(
            user_repository=self.fake_repo,
            logger=self.fake_logger,
            metrics=self.fake_metrics
        )

    def test_creates_user_with_cognitive_validation(self):
        """
        Cognitive test validating:
        - Intent matches outcome
        - Metrics collected
        - Logs structured
        - Performance acceptable
        """
        # 1. Captura intenção
        intent = "Create user named Alice with email alice@example.com"

        # 2. Executa
        output = self.usecase.execute(CreateUserInput(
            name="Alice",
            email="alice@example.com"
        ))

        # 3. Validações tradicionais
        self.assertEqual(output.name, "Alice")
        self.assertEqual(output.email, "alice@example.com")

        # 4. COGNITIVE: Valida intenção
        actual = f"Created user {output.name} with email {output.email}"
        self.assert_intent_matches(
            expected=intent,
            actual=actual,
            threshold=0.75  # 75% similarity mínima
        )

        # 5. COGNITIVE: Valida métricas
        self.assert_metrics_collected({
            'create_user.duration': lambda v: v > 0,
            'create_user.count': lambda v: v == 1
        })

        # 6. COGNITIVE: Valida logs estruturados
        logs = self.fake_logger.get_logs(level='info')
        self.assertTrue(any('user' in log['message'].lower() for log in logs))

        # 7. COGNITIVE: Valida performance
        self.assert_performance_within(
            lambda: self.usecase.execute(CreateUserInput(...)),
            max_duration_ms=50.0
        )

        # 8. Valida persistência
        self.assertEqual(self.fake_repo.count(), 1)
```

### Intent Tracking em Testes

```python
from forgebase.integration import IntentTracker


class TestWithIntentTracking(ForgeTestCase):
    def test_validates_coherence(self):
        """Test with full intent tracking."""
        tracker = IntentTracker()

        # Capture intent
        intent_id = tracker.capture_intent(
            description="Create user Alice",
            expected_outcome="User created successfully"
        )

        # Execute
        output = self.usecase.execute(CreateUserInput(...))

        # Record execution
        tracker.record_execution(
            intent_id=intent_id,
            actual_outcome=f"User {output.user_id} created",
            success=True
        )

        # Validate coherence
        report = tracker.validate_coherence(intent_id)

        # Assertions
        self.assertIn(report.coherence_level, [
            CoherenceLevel.PERFECT,
            CoherenceLevel.HIGH
        ])
        self.assertGreaterEqual(report.similarity_score, 0.80)
```

---

## 🛠️ Test Doubles: Fakes vs Mocks

ForgeBase prefere **Fakes** sobre Mocks.

### Fakes (Recomendado)

Implementações funcionais in-memory para testes.

```python
# Using Fakes
def test_with_fakes(self):
    fake_repo = FakeRepository()  # Real implementation, in-memory
    usecase = CreateUserUseCase(user_repository=fake_repo)

    output = usecase.execute(CreateUserInput(...))

    # Verify state
    self.assertEqual(fake_repo.count(), 1)
    user = fake_repo.find_by_id(output.user_id)
    self.assertIsNotNone(user)
```

**Vantagens:**
- Mais próximo do comportamento real
- Detecta bugs em interações
- Fácil inspecionar estado
- Menos frágil

### Mocks (Use com Moderação)

```python
from unittest.mock import Mock

# Using Mocks
def test_with_mocks(self):
    mock_repo = Mock(spec=UserRepositoryPort)
    mock_repo.find_by_email.return_value = None  # No duplicate

    usecase = CreateUserUseCase(user_repository=mock_repo)

    output = usecase.execute(CreateUserInput(...))

    # Verify interactions
    mock_repo.save.assert_called_once()
    mock_repo.find_by_email.assert_called_with("alice@example.com")
```

**Use quando:**
- Testar interações específicas
- Simular erros difíceis de reproduzir
- Verificar calls exatos

---

## 📊 Coverage

### Rodando Testes com Coverage

```bash
# Run all tests with coverage
pytest --cov=forgebase --cov-report=html

# Coverage report
open htmlcov/index.html
```

### Metas de Coverage

- **Domain Layer**: ≥95%
- **Application Layer**: ≥90%
- **Infrastructure Layer**: ≥80%
- **Adapters Layer**: ≥70%

---

## ⚡ Executando Testes

### Run All Tests

```bash
pytest
```

### Run Specific Test File

```bash
pytest tests/unit/domain/test_user.py
```

### Run Specific Test

```bash
pytest tests/unit/domain/test_user.py::TestUser::test_creates_user
```

### Run by Markers

```bash
# Fast tests only
pytest -m "not slow"

# Integration tests
pytest -m integration

# Cognitive tests
pytest -m cognitive
```

### Verbose Output

```bash
pytest -v
pytest -vv  # Extra verbose
```

### Stop on First Failure

```bash
pytest -x
```

---

## 🎯 Boas Práticas

### 1. One Assertion per Test (Ideal)

```python
# ✅ Good
def test_creates_user(self):
    output = usecase.execute(input_dto)
    self.assertIsNotNone(output.user_id)

def test_persists_user(self):
    usecase.execute(input_dto)
    self.assertEqual(repo.count(), 1)

# ⚠️ Acceptable for cognitive tests
def test_cognitive_validation(self):
    # Multiple related assertions OK
    self.assert_intent_matches(...)
    self.assert_metrics_collected(...)
    self.assert_performance_within(...)
```

### 2. Test Names são Documentação

```python
# ✅ Good: Describes behavior
def test_rejects_negative_price(self):
    ...

def test_marks_order_as_paid_when_payment_succeeds(self):
    ...

# ❌ Bad: Not descriptive
def test_price(self):
    ...

def test_order(self):
    ...
```

### 3. setUp() para Contexto Compartilhado

```python
class TestCreateUser(unittest.TestCase):
    def setUp(self):
        # Shared setup
        self.fake_repo = FakeRepository()
        self.usecase = CreateUserUseCase(user_repository=self.fake_repo)

    def test_case_1(self):
        # Uses self.usecase
        ...

    def test_case_2(self):
        # Uses self.usecase
        ...
```

### 4. tearDown() para Cleanup

```python
def setUp(self):
    self.temp_dir = tempfile.mkdtemp()

def tearDown(self):
    shutil.rmtree(self.temp_dir)
```

### 5. Docstrings em Testes

```python
def test_creates_user(self):
    """
    Test that CreateUserUseCase creates a user successfully.

    Given valid input (name and email)
    When execute() is called
    Then user should be created and persisted
    """
    ...
```

---

## 🐛 Debugging Testes

### Print Debugging

```python
def test_example(self):
    output = usecase.execute(input_dto)
    print(f"Output: {output.to_dict()}")  # Debug
    self.assertEqual(output.name, "Alice")
```

### pdb (Python Debugger)

```python
def test_example(self):
    import pdb; pdb.set_trace()  # Breakpoint
    output = usecase.execute(input_dto)
    self.assertEqual(output.name, "Alice")
```

### pytest --pdb

```bash
# Drop into debugger on failure
pytest --pdb
```

---

## 📚 Recursos Adicionais

- **[Example Cookbook](cookbook.md)** — Receitas práticas
- **[ADR-004: Cognitive Testing](adr/004-cognitive-testing.md)** — Filosofia
- **[Getting Started Guide](getting-started.md)** — Primeiros testes

---

**Teste com Propósito! 🧪**

*"Cada teste documenta intenção e valida coerência."*
