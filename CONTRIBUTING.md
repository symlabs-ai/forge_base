# Contributing to ForgeBase

> "Forjar é transformar pensamento em estrutura — juntos."

Obrigado pelo interesse em contribuir com ForgeBase! Este documento guia como contribuir de forma efetiva e alinhada com os princípios do projeto.

---

## 📜 Código de Conduta

ForgeBase adota princípios de **Reflexividade**, **Autonomia** e **Coerência Cognitiva**. Esperamos que contribuidores:

- Sejam respeitosos e construtivos em discussões
- Valorizem código claro e explicativo
- Priorizem arquitetura sobre quick fixes
- Documentem decisões (não apenas código)
- Testem não apenas comportamento, mas intenção

---

## 🚀 Como Contribuir

### 1. Reportar Bugs

**Antes de Reportar:**
- Verifique se o bug já foi reportado em [Issues](https://github.com/your-org/forgebase/issues)
- Confirme que é um bug (não comportamento esperado)
- Tente reproduzir em ambiente limpo

**Criando um Bug Report:**

```markdown
**Descrição do Bug:**
[Descrição clara do problema]

**Como Reproduzir:**
1. Crie entidade X com propriedade Y
2. Execute método Z
3. Observe erro

**Comportamento Esperado:**
[O que deveria acontecer]

**Comportamento Atual:**
[O que está acontecendo]

**Ambiente:**
- ForgeBase version: 1.0.0
- Python version: 3.11.0
- OS: Ubuntu 22.04

**Stacktrace:**
```
[Cole o stack trace completo]
```

**Código para Reproduzir:**
```python
# Código mínimo que reproduz o bug
```
```

### 2. Sugerir Funcionalidades

**Antes de Sugerir:**
- Verifique se a feature já foi sugerida
- Considere se alinha com filosofia ForgeBase (Clean Architecture, Observability First, etc.)
- Pense em alternativas

**Criando uma Feature Request:**

```markdown
**Problema que Resolve:**
[Qual problema esta feature resolve?]

**Solução Proposta:**
[Como você imagina que funcione]

**Alternativas Consideradas:**
[Outras formas de resolver o problema]

**Impacto na Arquitetura:**
[Como afeta Clean Architecture, Ports/Adapters, etc.]

**Exemplo de Uso:**
```python
# Como seria usar a feature
```
```

### 3. Contribuir com Código

#### Preparando o Ambiente

```bash
# Clone o repositório
git clone https://github.com/your-org/forgebase.git
cd forgebase

# Crie um ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instale dependências de desenvolvimento
pip install -e ".[dev]"

# Instale pre-commit hooks
pre-commit install
```

#### Workflow de Desenvolvimento

1. **Crie uma Branch**

```bash
git checkout -b feature/minha-feature
# ou
git checkout -b fix/meu-bugfix
```

Convenção de nomes:
- `feature/` — Nova funcionalidade
- `fix/` — Correção de bug
- `docs/` — Apenas documentação
- `refactor/` — Refatoração sem mudança de comportamento
- `test/` — Adição/melhoria de testes

2. **Escreva Código (TDD)**

```bash
# 1. Escreva o teste primeiro
vim tests/unit/domain/test_my_feature.py

# 2. Execute testes (deve falhar)
pytest tests/unit/domain/test_my_feature.py

# 3. Implemente a feature
vim src/forgebase/domain/my_feature.py

# 4. Execute testes (deve passar)
pytest tests/unit/domain/test_my_feature.py

# 5. Refatore
# ...

# 6. Execute toda a suite
pytest
```

3. **Escreva Docstrings reST**

```python
def my_function(param: str, value: int) -> bool:
    """
    [Uma linha descrevendo o que faz]

    [Parágrafo explicando POR QUÊ esta implementação,
    decisões de design, e contexto arquitetural]

    :param param: Description of param
    :type param: str
    :param value: Description of value
    :type value: int
    :return: Description of return value
    :rtype: bool
    :raises ValueError: When value is negative

    Example::

        >>> result = my_function("test", 42)
        >>> print(result)
        True

    See Also:
        - :class:`RelatedClass`
        - :func:`related_function`
    """
    pass
```

4. **Execute Linting**

```bash
# Ruff linting + formatting
ruff check .
ruff format .

# Type checking
mypy src/forgebase
```

5. **Execute Testes Completos**

```bash
# Todos os testes
pytest

# Com coverage
pytest --cov=forgebase --cov-report=html

# Testes específicos
pytest tests/unit/domain/

# Apenas testes rápidos
pytest -m "not slow"
```

6. **Commit com Mensagem Convencional**

```bash
git add .
git commit -m "feat: adiciona suporte para MongoDB Repository

Implementa MongoDBRepository que estende RepositoryBase
para permitir persistência em MongoDB.

- Adiciona MongoDBRepository em infrastructure/repository/
- Adiciona testes em tests/unit/infrastructure/
- Atualiza documentação no cookbook

Refs #123
"
```

**Formato de Commit:**

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: Nova feature
- `fix`: Bug fix
- `docs`: Apenas documentação
- `style`: Formatação (sem mudança de código)
- `refactor`: Refatoração sem mudança de comportamento
- `test`: Adição/mudança de testes
- `chore`: Tarefas de manutenção

**Exemplos:**

```bash
feat(domain): adiciona Money ValueObject
fix(repository): corrige race condition em save()
docs(adr): adiciona ADR-007 sobre caching
refactor(usecase): simplifica validação de input
test(integration): adiciona testes de YAML sync
```

7. **Push e Abra Pull Request**

```bash
git push origin feature/minha-feature
```

No GitHub:
- Abra Pull Request
- Preencha template (descrição, testes, screenshots se aplicável)
- Aguarde code review

---

## ✅ Checklist de Pull Request

Antes de submeter, verifique:

### Código

- [ ] Código segue Clean Architecture (dependências corretas)
- [ ] Ports e Adapters claramente separados
- [ ] Type hints completos
- [ ] Sem código comentado (remover ou documentar porquê)
- [ ] Sem print() statements (usar logger)
- [ ] Sem dependências circulares

### Testes

- [ ] Testes unitários escritos (≥90% coverage para novo código)
- [ ] Testes passam localmente (`pytest`)
- [ ] Testes cognitivos se aplicável (ForgeTestCase)
- [ ] Não quebra testes existentes

### Documentação

- [ ] Docstrings reST em todas as classes/métodos públicos
- [ ] Docstrings explicam "porquê", não apenas "o quê"
- [ ] Exemplos de uso incluídos
- [ ] README atualizado se necessário
- [ ] CHANGELOG.md atualizado (seção Unreleased)

### Observabilidade

- [ ] Logging estruturado adicionado se aplicável
- [ ] Métricas coletadas se aplicável
- [ ] Erro handling apropriado

### Decisões Arquiteturais

- [ ] ADR criado se decisão significativa
- [ ] Alternativas consideradas documentadas

---

## 🧪 Padrões de Teste

### Estrutura de Testes

```
tests/
├── unit/                    # Testes unitários (isolados)
│   ├── domain/
│   │   ├── test_entity.py
│   │   └── test_value_object.py
│   ├── application/
│   │   └── test_usecase.py
│   └── infrastructure/
│       └── test_repository.py
├── integration/             # Testes de integração
│   ├── test_yaml_sync.py
│   └── test_sql_repository.py
└── cognitive/              # Testes cognitivos
    └── test_create_user_cognitive.py
```

### Exemplo de Teste Unitário

```python
import unittest
from forgebase.domain import ValidationError


class TestUser(unittest.TestCase):
    """Unit tests for User entity."""

    def test_creates_user_with_valid_data(self):
        """Test user creation with valid data."""
        user = User(name="Alice", email="alice@example.com")

        self.assertEqual(user.name, "Alice")
        self.assertEqual(user.email, "alice@example.com")
        self.assertTrue(user.is_active)

    def test_rejects_empty_name(self):
        """Test that empty name is rejected."""
        with self.assertRaises(ValidationError) as ctx:
            User(name="", email="alice@example.com")

        self.assertIn("name cannot be empty", str(ctx.exception).lower())

    def test_validates_email_format(self):
        """Test email format validation."""
        with self.assertRaises(ValidationError):
            User(name="Alice", email="invalid-email")
```

### Exemplo de Teste Cognitivo

```python
from forgebase.testing import ForgeTestCase
from forgebase.testing.fakes import FakeRepository, FakeLogger


class TestCreateUserCognitive(ForgeTestCase):
    """Cognitive tests for CreateUser UseCase."""

    def test_creates_user_with_intent_validation(self):
        """Cognitive test validating intent, metrics, and performance."""
        # Setup
        fake_repo = FakeRepository()
        fake_logger = FakeLogger()
        usecase = CreateUserUseCase(
            user_repository=fake_repo,
            logger=fake_logger
        )

        # Intent
        intent = "Create user Alice with email alice@example.com"

        # Execute
        output = usecase.execute(CreateUserInput(
            name="Alice",
            email="alice@example.com"
        ))

        # Cognitive validations
        actual = f"Created user {output.name} with email {output.email}"
        self.assert_intent_matches(intent, actual, threshold=0.80)

        # Metrics validation
        self.assert_metrics_collected({
            'create_user.count': lambda v: v == 1
        })

        # Performance validation
        self.assert_performance_within(
            lambda: usecase.execute(CreateUserInput(...)),
            max_duration_ms=50.0
        )
```

---

## 📐 Padrões de Código

### Clean Architecture

**Regras de Dependência:**

```python
# ✅ OK: Application → Domain
from forgebase.domain import EntityBase

class CreateUserUseCase(UseCaseBase):
    pass

# ✅ OK: Infrastructure → Application
from forgebase.application import PortBase

class JSONRepository(PortBase):
    pass

# ❌ ERRADO: Domain → Application
from forgebase.application import UseCaseBase  # NÃO!

class User(EntityBase):
    pass

# ❌ ERRADO: Domain → Infrastructure
from forgebase.infrastructure import JSONRepository  # NÃO!

class User(EntityBase):
    pass
```

### Dependency Injection

**Sempre use constructor injection:**

```python
# ✅ Correto
class CreateUserUseCase(UseCaseBase):
    def __init__(
        self,
        user_repository: UserRepositoryPort,  # Port, não adapter
        logger: LoggerPort
    ):
        self.user_repository = user_repository
        self.logger = logger

# ❌ Errado
class CreateUserUseCase(UseCaseBase):
    def __init__(self):
        self.user_repository = JSONRepository()  # Acoplamento direto
        self.logger = StdoutLogger()
```

### Naming Conventions

```python
# Entities: Substantivos (singular)
class User(EntityBase): pass
class Order(EntityBase): pass

# ValueObjects: Substantivos compostos
class EmailAddress(ValueObjectBase): pass
class Money(ValueObjectBase): pass

# UseCases: Verbo + Substantivo + "UseCase"
class CreateUserUseCase(UseCaseBase): pass
class PlaceOrderUseCase(UseCaseBase): pass

# Ports: Substantivo + "Port"
class UserRepositoryPort(ABC): pass
class NotificationServicePort(ABC): pass

# Adapters: Tecnologia + Substantivo + "Adapter"
class JSONUserRepository(UserRepositoryPort): pass
class SMTPNotificationAdapter(NotificationServicePort): pass
class HTTPAdapter(AdapterBase): pass

# DTOs: UseCase + "Input"/"Output"
class CreateUserInput(DTOBase): pass
class CreateUserOutput(DTOBase): pass
```

### Error Handling

```python
# Domain errors
from forgebase.domain import ValidationError, BusinessRuleViolation

# ValidationError: Dados inválidos
if not email:
    raise ValidationError("Email cannot be empty")

# BusinessRuleViolation: Regra de negócio violada
if user_exists:
    raise BusinessRuleViolation(f"User with email {email} already exists")

# Application errors
from forgebase.application import UseCaseError

# UseCaseError: Erro de orquestração
if customer is None:
    raise UseCaseError(f"Customer not found: {customer_id}")
```

---

## 📝 Documentação

### ADRs (Architecture Decision Records)

Para decisões arquiteturais significativas, crie um ADR:

```bash
# Criar ADR
vim docs/adr/007-minha-decisao.md
```

**Template:**

```markdown
# ADR-007: [Título da Decisão]

## Status

**Proposta** | **Aceita** | **Superseded**

## Context

[Contexto e problema que motivou a decisão]

## Decision

[Decisão tomada]

## Consequences

### Positivas
- ✅ Benefício 1
- ✅ Benefício 2

### Negativas
- ⚠️ Trade-off 1
- ⚠️ Trade-off 2

## Alternatives Considered

### Alternativa 1
[Por que foi rejeitada]

### Alternativa 2
[Por que foi rejeitada]

## References

- Link 1
- Link 2
```

---

## 🔄 Processo de Review

### Para Reviewers

**O que avaliar:**

1. **Arquitetura**
   - Clean Architecture respeitada?
   - Dependências corretas?
   - Ports/Adapters apropriados?

2. **Código**
   - Legibilidade e clareza
   - Type hints completos
   - Sem code smells

3. **Testes**
   - Coverage adequado
   - Testes passam
   - Casos edge cobertos

4. **Documentação**
   - Docstrings presentes e completos
   - Exemplos claros
   - ADR se necessário

**Como dar feedback:**

```markdown
# ✅ Bom feedback (construtivo)
"Boa implementação! Sugiro extrair essa validação para um validator reutilizável, pois pode ser útil em outros lugares. Exemplo: `DomainValidators.validate_email()`"

# ❌ Feedback ruim (não construtivo)
"Isso está errado."
```

### Para Autores

**Respondendo a feedback:**

- Seja receptivo
- Pergunte se não entender
- Não leve para o pessoal
- Agradeça o tempo do reviewer

**Iterando:**

```bash
# Fazer mudanças solicitadas
vim src/forgebase/domain/my_feature.py

# Commit com referência ao PR
git commit -m "fix: corrige validação conforme feedback do review

Ref #45 (comment)
"

# Push atualizado
git push origin feature/minha-feature
```

---

## 🎓 Recursos para Contribuidores

### Documentação

- **[Getting Started](docs/getting-started.md)** — Tutorial inicial
- **[Cookbook](docs/cookbook.md)** — Receitas práticas
- **[ADRs](docs/adr/)** — Decisões arquiteturais
- **[Testing Guide](docs/testing-guide.md)** — Como testar

### Exemplos

- `examples/complete_flow.py` — Exemplo completo
- `examples/user_management/` — App de exemplo

### Leituras Recomendadas

- **Clean Architecture** by Robert C. Martin
- **Domain-Driven Design** by Eric Evans
- **Hexagonal Architecture** by Alistair Cockburn
- **Growing Object-Oriented Software, Guided by Tests** by Freeman & Pryce

---

## 🐛 Reportando Security Issues

**NÃO** abra issue pública para problemas de segurança.

Envie email para: security@forgebase.dev

Include:
- Descrição da vulnerabilidade
- Steps to reproduce
- Potencial impacto
- Sugestão de fix (se tiver)

---

## 💬 Comunidade

- **GitHub Discussions:** Para perguntas e discussões
- **GitHub Issues:** Para bugs e features
- **Pull Requests:** Para contribuições de código

---

## ❓ FAQ

**P: Posso contribuir se não sou expert em Clean Architecture?**
R: Sim! Leia os ADRs e exemplos. Pedimos ajuda durante review.

**P: Meu PR foi rejeitado. E agora?**
R: Leia o feedback, pergunte se não entender, e itere. Nem todo PR é aceito na primeira tentativa.

**P: Posso contribuir apenas com documentação?**
R: Absolutamente! Docs são tão importantes quanto código.

**P: Como sei se uma feature será aceita?**
R: Abra uma issue de discussão antes de implementar. Podemos validar alinhamento com roadmap.

**P: Posso usar lib X no meu PR?**
R: Preferimos zero dependências externas. Se absolutamente necessário, justifique na discussão.

---

## 📜 Licença

Ao contribuir com ForgeBase, você concorda que suas contribuições serão licenciadas sob a mesma licença do projeto (MIT License).

---

**Obrigado por contribuir! 🔨**

*"Cada contribuição forja o futuro do framework."*
