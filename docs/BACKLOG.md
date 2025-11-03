# ForgeBase — Backlog de Desenvolvimento

> "Forjar é transformar pensamento em estrutura."

Este documento organiza todas as etapas de desenvolvimento do **ForgeBase**, o núcleo técnico do Forge Framework. Cada item reflete os princípios de **Reflexividade**, **Autonomia** e **Coerência Cognitiva**.

---

## 📊 Visão Geral

### Objetivo
Implementar uma arquitetura cognitiva completa que:
- **Pensa**: Código com intenção e propósito claros
- **Mede**: Observabilidade nativa em todos os níveis
- **Explica**: Capacidade de auto-reflexão e documentação viva

### Princípios de Desenvolvimento
- **Clean Architecture** + **Hexagonal Architecture**
- **Test-Driven Development** com testes cognitivos
- **Observabilidade First** — métricas desde o início
- **Zero dependências circulares**
- **Docstrings reST explicando "porquê", não apenas "o quê"**

### Critérios de Sucesso Globais
✅ Modularização: 100% dos módulos com `from forgebase.[module]`
✅ Cobertura de testes: ≥90% dos módulos core
✅ Observabilidade: 100% de UseCases/Ports instrumentados
✅ Desacoplamento: 0 dependências proibidas entre camadas
✅ Extensibilidade: Novos adapters sem modificar o core

---

## 🎯 Matriz de Prioridades

| Prioridade | Descrição | Timeline | Fase |
|------------|-----------|----------|------|
| **P0 - Crítico** | Base classes, estrutura, observabilidade básica | Semana 1 | Fase 1 |
| **P1 - Alto** | Repository, config, testes, decorators | Semana 2 | Fases 2-4 |
| **P2 - Médio** | Adapters, core init, exemplos | Semanas 3-4 | Fases 5-6 |
| **P3 - Baixo** | Integrações avançadas, docs estendidas | Semana 5+ | Fases 7-8 |

---

## 🏗️ FASE 1: Fundação & Arquitetura Core

**Prioridade:** P0 (Crítico)
**Dependências:** Nenhuma
**Timeline:** Dias 1-3

### 1.1 Estrutura de Diretórios

**Tarefa:** Criar toda a estrutura de pastas do framework

**Diretórios a criar:**
```
src/forgebase/
├── domain/
│   ├── __init__.py
│   └── validators/
│       └── __init__.py
├── application/
│   ├── __init__.py
│   └── decorators/
│       └── __init__.py
├── adapters/
│   ├── __init__.py
│   ├── cli/
│   │   └── __init__.py
│   ├── http/
│   │   └── __init__.py
│   └── ai/
│       └── __init__.py
├── infrastructure/
│   ├── __init__.py
│   ├── repository/
│   │   └── __init__.py
│   ├── logging/
│   │   └── __init__.py
│   ├── configuration/
│   │   └── __init__.py
│   └── security/
│       └── __init__.py
├── observability/
│   └── __init__.py
└── testing/
    ├── __init__.py
    ├── fakes/
    │   └── __init__.py
    └── fixtures/
        └── __init__.py
```

**Critérios de Aceite:**
- [ ] Todas as pastas criadas
- [ ] Todos os `__init__.py` presentes
- [ ] Imports modulares funcionando
- [ ] Python 3.11+ configurado

---

### 1.2 Base Classes — Domain Layer

#### 1.2.1 EntityBase

**Arquivo:** `src/forgebase/domain/entity_base.py`
**Prioridade:** P0
**Complexidade:** Média

**Descrição:**
Classe base abstrata para todas as entidades de domínio.

**Responsabilidades:**
- Gestão de identidade (ID)
- Enforcement de invariantes
- Independência de infraestrutura
- Validação de estado

**Interface Mínima:**
```python
class EntityBase(ABC):
    def __init__(self, id: Optional[str] = None)
    @abstractmethod
    def validate(self) -> None
    def __eq__(self, other) -> bool
    def __hash__(self) -> int
```

**Critérios de Aceite:**
- [ ] Classe abstrata implementada
- [ ] Gestão de ID única
- [ ] Método `validate()` abstrato
- [ ] Igualdade baseada em ID
- [ ] Docstring reST completa explicando propósito
- [ ] Testes unitários (≥90% coverage)

---

#### 1.2.2 ValueObjectBase

**Arquivo:** `src/forgebase/domain/value_object_base.py`
**Prioridade:** P0
**Complexidade:** Baixa

**Descrição:**
Classe base para objetos de valor imutáveis.

**Responsabilidades:**
- Imutabilidade garantida
- Igualdade estrutural (não por ID)
- Validação de valores
- Sem identidade própria

**Interface Mínima:**
```python
class ValueObjectBase(ABC):
    def __init__(self, **kwargs)
    @abstractmethod
    def validate(self) -> None
    def __eq__(self, other) -> bool
    def __hash__(self) -> int
    def to_dict(self) -> dict
```

**Critérios de Aceite:**
- [ ] Imutabilidade enforçada
- [ ] Igualdade estrutural
- [ ] Validação implementada
- [ ] Serialização para dict
- [ ] Docstring reST completa
- [ ] Testes unitários (≥90% coverage)

---

#### 1.2.3 Domain Exceptions

**Arquivo:** `src/forgebase/domain/exceptions.py`
**Prioridade:** P0
**Complexidade:** Baixa

**Descrição:**
Hierarquia de exceções específicas do domínio.

**Exceções a criar:**
- `DomainException` (base)
- `ValidationError`
- `InvariantViolation`
- `BusinessRuleViolation`

**Critérios de Aceite:**
- [ ] Hierarquia clara de exceções
- [ ] Mensagens descritivas
- [ ] Context information nos erros
- [ ] Docstring explicando quando usar cada uma
- [ ] Exemplos de uso
- [ ] Testes de criação e propagação

---

#### 1.2.4 Domain Validators

**Arquivo:** `src/forgebase/domain/validators/rules.py`
**Prioridade:** P0
**Complexidade:** Média

**Descrição:**
Validadores e regras de negócio reutilizáveis.

**Componentes:**
- Validadores básicos (not_null, not_empty, range, pattern)
- Composição de validadores
- Mensagens de erro contextuais

**Critérios de Aceite:**
- [ ] Validadores básicos implementados
- [ ] Composição de regras funcional
- [ ] Mensagens de erro claras
- [ ] Docstring explicando filosofia de validação
- [ ] Testes cobrindo casos edge
- [ ] Exemplos de uso no domínio

---

### 1.3 Base Classes — Application Layer

#### 1.3.1 UseCaseBase

**Arquivo:** `src/forgebase/application/usecase_base.py`
**Prioridade:** P0
**Complexidade:** Alta

**Descrição:**
Classe base abstrata para todos os casos de uso (ValueTracks).

**Responsabilidades:**
- Orquestração de lógica de aplicação
- Interface com ports
- Hooks para observabilidade
- Tratamento de erros

**Interface Mínima:**
```python
class UseCaseBase(ABC):
    @abstractmethod
    def execute(self, *args, **kwargs) -> Any
    def _before_execute(self) -> None
    def _after_execute(self) -> None
    def _on_error(self, error: Exception) -> None
```

**Critérios de Aceite:**
- [ ] Classe abstrata com método `execute()`
- [ ] Hooks para lifecycle (before/after/error)
- [ ] Integração com métricas (preparado para decorators)
- [ ] Docstring explicando padrão de orquestração
- [ ] Exemplo de implementação concreta
- [ ] Testes de lifecycle hooks
- [ ] Cobertura ≥90%

---

#### 1.3.2 PortBase

**Arquivo:** `src/forgebase/application/port_base.py`
**Prioridade:** P0
**Complexidade:** Média

**Descrição:**
Interface base para contratos de comunicação externa (Ports).

**Responsabilidades:**
- Definir contratos claros
- Método `info()` para introspecção
- Documentação de semântica do contrato

**Interface Mínima:**
```python
class PortBase(ABC):
    @abstractmethod
    def info(self) -> dict
    def __str__(self) -> str
```

**Critérios de Aceite:**
- [ ] Interface abstrata clara
- [ ] Método `info()` retornando estrutura padronizada
- [ ] Docstring explicando filosofia de Ports
- [ ] Exemplo de Port concreto
- [ ] Testes de introspecção
- [ ] Documentação sobre driving vs driven ports

---

#### 1.3.3 DTOBase

**Arquivo:** `src/forgebase/application/dto_base.py`
**Prioridade:** P1
**Complexidade:** Baixa

**Descrição:**
Base para Data Transfer Objects padronizados.

**Responsabilidades:**
- Transferência de dados entre camadas
- Validação de dados de entrada/saída
- Serialização/deserialização

**Interface Mínima:**
```python
class DTOBase(ABC):
    @abstractmethod
    def validate(self) -> None
    def to_dict(self) -> dict
    @classmethod
    def from_dict(cls, data: dict) -> Self
```

**Critérios de Aceite:**
- [ ] Classe base implementada
- [ ] Validação automática
- [ ] Serialização bidirecional (to/from dict)
- [ ] Type hints completos
- [ ] Docstring explicando uso
- [ ] Testes de serialização/deserialização

---

#### 1.3.4 Error Handling

**Arquivo:** `src/forgebase/application/error_handling.py`
**Prioridade:** P1
**Complexidade:** Média

**Descrição:**
Sistema padronizado de tratamento de erros na aplicação.

**Componentes:**
- Exception guards
- Error context propagation
- Logging integration
- Error mapping (domain → application)

**Critérios de Aceite:**
- [ ] Guards para erros comuns
- [ ] Context propagation funcional
- [ ] Integração com logging
- [ ] Mapeamento domain → application errors
- [ ] Docstring explicando estratégia
- [ ] Testes de cenários de erro

---

### 1.4 Base Classes — Adapters Layer

#### 1.4.1 AdapterBase

**Arquivo:** `src/forgebase/adapters/adapter_base.py`
**Prioridade:** P0
**Complexidade:** Média

**Descrição:**
Classe base para todos os adapters (driving e driven).

**Responsabilidades:**
- Introspecção (nome, módulo)
- Hooks para instrumentação
- Padrão comum para todos adapters

**Interface Mínima:**
```python
class AdapterBase(ABC):
    @abstractmethod
    def name(self) -> str
    @abstractmethod
    def module(self) -> str
    def info(self) -> dict
    def _instrument(self) -> None
```

**Critérios de Aceite:**
- [ ] Classe abstrata implementada
- [ ] Métodos de introspecção
- [ ] Hook para feedback/instrumentation
- [ ] Docstring explicando driving vs driven adapters
- [ ] Exemplo de adapter concreto
- [ ] Testes de introspecção

---

## 🔧 FASE 2: Infraestrutura & Serviços Técnicos

**Prioridade:** P1 (Alto)
**Dependências:** Fase 1 (Base Classes)
**Timeline:** Dias 4-7

### 2.1 Repository Layer

#### 2.1.1 RepositoryBase

**Arquivo:** `src/forgebase/infrastructure/repository/repository_base.py`
**Prioridade:** P1
**Complexidade:** Média

**Descrição:**
Interface abstrata para persistência de entidades.

**Responsabilidades:**
- Contrato CRUD padronizado
- Independência de tecnologia
- Query interface

**Interface Mínima:**
```python
class RepositoryBase(ABC, Generic[T]):
    @abstractmethod
    def save(self, entity: T) -> None
    @abstractmethod
    def find_by_id(self, id: str) -> Optional[T]
    @abstractmethod
    def find_all(self) -> List[T]
    @abstractmethod
    def delete(self, id: str) -> None
    @abstractmethod
    def exists(self, id: str) -> bool
```

**Critérios de Aceite:**
- [ ] Interface genérica com typing
- [ ] CRUD completo
- [ ] Docstring explicando padrão Repository
- [ ] Exemplo de implementação
- [ ] Testes com mock implementation

---

#### 2.1.2 JSONRepository

**Arquivo:** `src/forgebase/infrastructure/repository/json_repository.py`
**Prioridade:** P1
**Complexidade:** Média

**Descrição:**
Implementação de Repository baseada em arquivos JSON.

**Responsabilidades:**
- Persistência em JSON
- Serialização de entidades
- Query simples

**Critérios de Aceite:**
- [ ] Implementa RepositoryBase
- [ ] CRUD funcional com arquivos JSON
- [ ] Serialização/deserialização de entidades
- [ ] Thread-safe operations
- [ ] Testes com temp directory
- [ ] Tratamento de erros de I/O

---

#### 2.1.3 SQLRepository

**Arquivo:** `src/forgebase/infrastructure/repository/sql_repository.py`
**Prioridade:** P2
**Complexidade:** Alta

**Descrição:**
Implementação de Repository baseada em SQL.

**Responsabilidades:**
- Persistência SQL
- Suporte a SQLAlchemy/similar
- Migrations
- Transações

**Critérios de Aceite:**
- [ ] Implementa RepositoryBase
- [ ] CRUD com SQL
- [ ] Suporte a transações
- [ ] Connection pooling
- [ ] Testes com SQLite in-memory
- [ ] Migration strategy documentada

---

### 2.2 Configuration Management

#### 2.2.1 ConfigLoader

**Arquivo:** `src/forgebase/infrastructure/configuration/config_loader.py`
**Prioridade:** P1
**Complexidade:** Média

**Descrição:**
Sistema de carregamento e gestão de configurações.

**Responsabilidades:**
- Carregar configs de múltiplas fontes (YAML, JSON, ENV)
- Configs por ambiente
- Validação de configuração
- Hot-reload (opcional)

**Fontes suportadas:**
- Arquivos YAML/JSON
- Variáveis de ambiente
- Argumentos de linha de comando
- Defaults hardcoded

**Critérios de Aceite:**
- [ ] Múltiplas fontes de config
- [ ] Precedência clara (ENV > file > defaults)
- [ ] Validação de schema
- [ ] Type-safe access
- [ ] Docstring explicando estratégia
- [ ] Testes com configs de exemplo

---

### 2.3 Logging Infrastructure

#### 2.3.1 LoggerPort

**Arquivo:** `src/forgebase/infrastructure/logging/logger_port.py`
**Prioridade:** P1
**Complexidade:** Baixa

**Descrição:**
Port (interface) para logging, permitindo múltiplas implementações.

**Responsabilidades:**
- Interface de logging padronizada
- Níveis de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Structured logging support
- Context propagation

**Interface Mínima:**
```python
class LoggerPort(ABC):
    @abstractmethod
    def debug(self, message: str, **context) -> None
    @abstractmethod
    def info(self, message: str, **context) -> None
    @abstractmethod
    def warning(self, message: str, **context) -> None
    @abstractmethod
    def error(self, message: str, **context) -> None
    @abstractmethod
    def critical(self, message: str, **context) -> None
```

**Critérios de Aceite:**
- [ ] Interface completa com todos os níveis
- [ ] Suporte a context (structured logging)
- [ ] Docstring explicando filosofia de logging
- [ ] Exemplo de implementação (StdoutLogger)
- [ ] Testes com fake logger

---

### 2.4 Security Layer

#### 2.4.1 Sandbox

**Arquivo:** `src/forgebase/infrastructure/security/sandbox.py`
**Prioridade:** P2
**Complexidade:** Alta

**Descrição:**
Sistema de execução isolada de código (sandbox).

**Responsabilidades:**
- Isolamento de execução
- Gestão de permissões
- Resource limits (CPU, memória, tempo)
- Política de segurança

**Critérios de Aceite:**
- [ ] Execução isolada funcional
- [ ] Timeouts configuráveis
- [ ] Resource limits
- [ ] Exception handling
- [ ] Docstring sobre use cases
- [ ] Testes com código malicioso simulado
- [ ] ⚠️ Documentar limitações de segurança

---

## 📊 FASE 3: Sistema de Observabilidade

**Prioridade:** P0/P1 (Crítico/Alto)
**Dependências:** Fase 1 (Base Classes)
**Timeline:** Dias 4-6

### 3.1 Core Observability

#### 3.1.1 LogService

**Arquivo:** `src/forgebase/observability/log_service.py`
**Prioridade:** P0
**Complexidade:** Alta

**Descrição:**
Serviço central de logging estruturado e agregação.

**Responsabilidades:**
- Logging estruturado (JSON output)
- Múltiplos handlers (stdout, file, remote)
- Context propagation
- Log aggregation
- Correlation IDs

**Features:**
- Structured data (não apenas strings)
- Automatic context injection
- Performance tracking
- Error stack traces
- Sampling para high-volume logs

**Critérios de Aceite:**
- [ ] Logging estruturado funcional
- [ ] Múltiplos outputs
- [ ] Context propagation automático
- [ ] Correlation ID tracking
- [ ] Configuração por arquivo
- [ ] Docstring explicando arquitetura
- [ ] Testes com múltiplos handlers
- [ ] Performance benchmarks

---

#### 3.1.2 TrackMetrics

**Arquivo:** `src/forgebase/observability/track_metrics.py`
**Prioridade:** P0
**Complexidade:** Alta

**Descrição:**
Sistema de coleta e telemetria de métricas.

**Responsabilidades:**
- Coleta de métricas (counters, gauges, histograms)
- Tracking de performance
- Success/failure rates
- Duration measurement
- Exportação de métricas

**Interface Mínima:**
```python
class TrackMetrics:
    def start(self, name: str, **labels) -> None
    def stop(self, name: str, **labels) -> None
    def increment(self, name: str, value: int = 1, **labels) -> None
    def gauge(self, name: str, value: float, **labels) -> None
    def histogram(self, name: str, value: float, **labels) -> None
    def report(self) -> dict
```

**Métricas Padrão:**
- `usecase.execution.duration` (histogram)
- `usecase.execution.count` (counter)
- `usecase.execution.errors` (counter)
- `port.call.duration` (histogram)
- `adapter.request.count` (counter)

**Critérios de Aceite:**
- [ ] Tipos de métricas implementados (counter, gauge, histogram)
- [ ] Context manager para durations
- [ ] Labels/tags support
- [ ] Aggregation funcional
- [ ] Export em formato Prometheus/JSON
- [ ] Docstring explicando tipos de métricas
- [ ] Testes de coleta e aggregation
- [ ] Performance overhead < 1ms per metric

---

#### 3.1.3 TracerPort

**Arquivo:** `src/forgebase/observability/tracer_port.py`
**Prioridade:** P1
**Complexidade:** Média

**Descrição:**
Port para distributed tracing (OpenTelemetry-compatible).

**Responsabilidades:**
- Interface de tracing
- Span creation e management
- Trace context propagation
- Baggage support

**Interface Mínima:**
```python
class TracerPort(ABC):
    @abstractmethod
    def start_span(self, name: str, **attributes) -> Span
    @abstractmethod
    def current_span(self) -> Optional[Span]
    @abstractmethod
    def inject_context(self) -> dict
    @abstractmethod
    def extract_context(self, carrier: dict) -> None
```

**Critérios de Aceite:**
- [ ] Interface compatível com OpenTelemetry
- [ ] Span lifecycle management
- [ ] Context propagation
- [ ] Docstring explicando distributed tracing
- [ ] Exemplo de implementação (NoOpTracer, JaegerTracer)
- [ ] Testes com mock tracer

---

#### 3.1.4 FeedbackManager

**Arquivo:** `src/forgebase/observability/feedback_manager.py`
**Prioridade:** P1
**Complexidade:** Alta

**Descrição:**
Gestão de feedback loops entre ForgeProcess ↔ ForgeBase.

**Responsabilidades:**
- Captura de intenção (ForgeProcess)
- Tracking de execução (ForgeBase)
- Mapeamento intenção → execução
- Learning data collection
- Cognitive coherence validation

**Features:**
- Intent tracking
- Execution trace mapping
- Decision point recording
- Feedback loops para ForgeProcess
- YAML sync preparation

**Critérios de Aceite:**
- [ ] Intent capture funcional
- [ ] Execution trace completo
- [ ] Mapeamento intenção-execução
- [ ] Export de learning data
- [ ] Docstring explicando filosofia cognitiva
- [ ] Testes de feedback loop completo
- [ ] Exemplo de uso com UseCase

---

### 3.2 Instrumentation Decorators

#### 3.2.1 @track_metrics Decorator

**Arquivo:** `src/forgebase/application/decorators/track_metrics.py`
**Prioridade:** P1
**Complexidade:** Média

**Descrição:**
Decorator para instrumentação automática de métricas.

**Uso:**
```python
@track_metrics(name="my_usecase")
def execute(self, input: dto) -> output:
    # ... lógica
```

**Features:**
- Auto-instrumentação de UseCases
- Tracking de duração
- Success/error counting
- Context propagation
- Labels automáticos (usecase name, module)

**Critérios de Aceite:**
- [ ] Decorator funcional
- [ ] Métricas automáticas coletadas
- [ ] Error tracking
- [ ] Overhead mínimo
- [ ] Docstring com exemplos
- [ ] Testes com UseCases mock
- [ ] Compatível com async functions

---

## 🧪 FASE 4: Infraestrutura de Testes

**Prioridade:** P1 (Alto)
**Dependências:** Fase 1, Fase 3 (Observability)
**Timeline:** Dias 5-7

### 4.1 Testing Base Classes

#### 4.1.1 ForgeTestCase

**Arquivo:** `src/forgebase/testing/forge_test_case.py`
**Prioridade:** P1
**Complexidade:** Alta

**Descrição:**
Classe base para testes cognitivos que documentam intenção.

**Responsabilidades:**
- Extends unittest.TestCase
- Assertions customizadas
- Setup/teardown com context
- Validação de métricas
- Validação de intenção

**Features Especiais:**
- `assert_intent_matches(expected, actual)` — valida coerência cognitiva
- `assert_metrics_collected(usecase, expected_metrics)` — valida instrumentação
- `assert_no_side_effects()` — valida pureza
- Context managers para isolamento

**Interface Adicional:**
```python
class ForgeTestCase(unittest.TestCase):
    def assert_intent_matches(self, expected: str, actual: str) -> None
    def assert_metrics_collected(self, metrics: dict) -> None
    def assert_no_side_effects(self, fn: Callable) -> None
    def setup_context(self, **kwargs) -> None
```

**Critérios de Aceite:**
- [ ] Extends unittest.TestCase
- [ ] Assertions cognitivas implementadas
- [ ] Context management
- [ ] Helpers para setup comum
- [ ] Docstring explicando testes cognitivos
- [ ] Exemplos de uso
- [ ] Self-testing (testes dos testes)

---

### 4.2 Test Doubles & Fixtures

#### 4.2.1 FakeLogger

**Arquivo:** `src/forgebase/testing/fakes/fake_logger.py`
**Prioridade:** P1
**Complexidade:** Baixa

**Descrição:**
Logger in-memory para testes.

**Responsabilidades:**
- Implementa LoggerPort
- Armazena logs em memória
- Métodos de inspeção
- Reset entre testes

**Features:**
- `get_logs(level: str) -> List[dict]`
- `assert_logged(message: str, level: str)`
- `clear()`

**Critérios de Aceite:**
- [ ] Implementa LoggerPort
- [ ] Storage in-memory
- [ ] Métodos de inspeção
- [ ] Thread-safe
- [ ] Docstring com exemplos
- [ ] Testes do fake

---

#### 4.2.2 FakeRepository

**Arquivo:** `src/forgebase/testing/fakes/fake_repository.py`
**Prioridade:** P1
**Complexidade:** Baixa

**Descrição:**
Repository in-memory para testes.

**Responsabilidades:**
- Implementa RepositoryBase
- Storage em dicionário
- Reset entre testes

**Critérios de Aceite:**
- [ ] Implementa RepositoryBase
- [ ] CRUD funcional em memória
- [ ] Métodos de inspeção (count, contains)
- [ ] Docstring com exemplos
- [ ] Testes do fake

---

#### 4.2.3 FakeMetricsCollector

**Arquivo:** `src/forgebase/testing/fakes/fake_metrics_collector.py`
**Prioridade:** P1
**Complexidade:** Baixa

**Descrição:**
Coletor de métricas in-memory para testes.

**Features:**
- Coleta métricas sem overhead
- Inspeção de métricas coletadas
- Assertions helpers

**Critérios de Aceite:**
- [ ] Storage in-memory
- [ ] Métodos de inspeção
- [ ] Reset funcional
- [ ] Docstring com exemplos
- [ ] Testes do fake

---

#### 4.2.4 Sample Data & Fixtures

**Arquivo:** `src/forgebase/testing/fixtures/sample_data.py`
**Prioridade:** P1
**Complexidade:** Baixa

**Descrição:**
Geração de dados de teste reutilizáveis.

**Componentes:**
- Entity factories
- DTO factories
- Test data builders
- Regression test fixtures

**Critérios de Aceite:**
- [ ] Factories para entidades comuns
- [ ] Builders com fluent interface
- [ ] Fixtures JSON para testes de regressão
- [ ] Docstring com exemplos
- [ ] Seed configurável para reproduzibilidade

---

## 🔌 FASE 5: Implementações de Adapters

**Prioridade:** P2 (Médio)
**Dependências:** Fases 1-3
**Timeline:** Dias 8-12

### 5.1 CLI Adapter

#### 5.1.1 CLIAdapter

**Arquivo:** `src/forgebase/adapters/cli/cli_adapter.py`
**Prioridade:** P2
**Complexidade:** Alta

**Descrição:**
Interface de linha de comando para ForgeBase.

**Responsabilidades:**
- Parsing de argumentos
- Comandos interativos
- Output formatado (tabelas, JSON, YAML)
- Help system automático
- Autocomplete support

**Comandos Básicos:**
- `forgebase run <usecase> [args]`
- `forgebase list usecases`
- `forgebase describe <usecase>`
- `forgebase metrics`
- `forgebase config`

**Features:**
- Click ou argparse
- Rich output (cores, tabelas)
- Progress bars
- Confirmações interativas

**Critérios de Aceite:**
- [ ] Parsing de comandos funcional
- [ ] Help automático gerado
- [ ] Output formatado (rich/tabulate)
- [ ] Error handling user-friendly
- [ ] Docstring com exemplos
- [ ] Testes com IO mocking
- [ ] Cobertura ≥80%

---

### 5.2 HTTP Adapter

#### 5.2.1 HTTPAdapter

**Arquivo:** `src/forgebase/adapters/http/http_adapter.py`
**Prioridade:** P2
**Complexidade:** Alta

**Descrição:**
API REST para expor UseCases via HTTP.

**Responsabilidades:**
- Endpoints REST padronizados
- Request/response handling
- Middleware support
- Authentication integration
- OpenAPI/Swagger docs

**Endpoints Básicos:**
- `POST /usecases/{name}/execute` — executa UseCase
- `GET /usecases` — lista UseCases disponíveis
- `GET /usecases/{name}` — descreve UseCase
- `GET /metrics` — retorna métricas
- `GET /health` — health check

**Stack Sugerida:**
- FastAPI ou Flask
- Pydantic para validação
- OpenAPI automatic docs

**Critérios de Aceite:**
- [ ] Endpoints REST funcionais
- [ ] Request validation (Pydantic)
- [ ] Error handling padronizado
- [ ] OpenAPI docs gerados
- [ ] Middleware de logging/metrics
- [ ] Docstring com exemplos
- [ ] Testes com TestClient
- [ ] Cobertura ≥80%

---

### 5.3 AI/LLM Adapter

#### 5.3.1 LLMAdapter

**Arquivo:** `src/forgebase/adapters/ai/llm_adapter.py`
**Prioridade:** P3
**Complexidade:** Alta

**Descrição:**
Interface para integração com LLMs (OpenAI, Anthropic, etc).

**Responsabilidades:**
- Gestão de prompts
- Parsing de respostas
- Context window management
- Token tracking
- Retry logic

**Features:**
- Template system para prompts
- Response parsing (JSON, text)
- Streaming support
- Cost tracking
- Multiple provider support

**Providers:**
- OpenAI (GPT-4, GPT-3.5)
- Anthropic (Claude)
- Local models (via Ollama/similar)

**Critérios de Aceite:**
- [ ] Provider abstraction funcional
- [ ] Prompt templating
- [ ] Response parsing robusto
- [ ] Token tracking
- [ ] Error handling e retries
- [ ] Docstring com exemplos
- [ ] Testes com mock LLM
- [ ] Exemplo de integração

---

## 🚀 FASE 6: Inicialização Core & Bootstrap

**Prioridade:** P2 (Médio)
**Dependências:** Todas as fases anteriores
**Timeline:** Dias 11-13

### 6.1 Core Initialization

#### 6.1.1 core_init.py

**Arquivo:** `src/forgebase/core_init.py`
**Prioridade:** P2
**Complexidade:** Alta

**Descrição:**
Sistema de bootstrap e inicialização cognitiva do ForgeBase.

**Responsabilidades:**
- Sequência de inicialização modular
- Dependency injection setup
- Configuration loading
- Observability activation
- Health checks
- Graceful startup/shutdown

**Fases de Bootstrap:**
1. **Load Configuration** — ConfigLoader
2. **Setup Logging** — LogService
3. **Initialize Observability** — TrackMetrics, Tracer
4. **Register UseCases** — UseCase discovery
5. **Initialize Adapters** — CLI, HTTP, AI
6. **Health Check** — Validar componentes
7. **Ready** — Sistema pronto

**Interface:**
```python
class ForgeBaseCore:
    def __init__(self, config_path: Optional[str] = None)
    def bootstrap(self) -> None
    def shutdown(self) -> None
    def get_usecase(self, name: str) -> UseCaseBase
    def list_usecases(self) -> List[str]
    def health_check(self) -> dict
```

**Critérios de Aceite:**
- [ ] Bootstrap sequence funcional
- [ ] Dependency injection working
- [ ] Config loading automático
- [ ] Health checks funcionais
- [ ] Graceful shutdown
- [ ] Docstring explicando arquitetura
- [ ] Testes de inicialização completa
- [ ] Exemplo de uso

---

## 🔗 FASE 7: Integração & Validação

**Prioridade:** P2/P3 (Médio/Baixo)
**Dependências:** Todas as fases
**Timeline:** Dias 14-18

### 7.1 Example Implementations

#### 7.1.1 Complete Example Flow

**Arquivo:** `examples/complete_flow.py`
**Prioridade:** P2
**Complexidade:** Média

**Descrição:**
Exemplo completo demonstrando todo o fluxo ForgeBase.

**Componentes do Exemplo:**
- Domain Entity (exemplo: `User`)
- Domain ValueObject (exemplo: `Email`)
- UseCase (exemplo: `CreateUserUseCase`)
- Port (exemplo: `UserRepositoryPort`)
- Adapter (exemplo: `CLIUserAdapter`)
- Tests (exemplo: `TestCreateUser`)

**Flow demonstrado:**
```
CLI Adapter → UseCase → Domain Logic → Port → Repository Adapter
     ↓
Observability (Logs, Metrics, Traces)
     ↓
Tests (Unit, Integration, Cognitive)
```

**Critérios de Aceite:**
- [ ] Exemplo completo funcional
- [ ] README explicando o exemplo
- [ ] Todos os layers representados
- [ ] Observabilidade visível
- [ ] Testes incluídos
- [ ] Instruções de execução

---

### 7.2 ForgeProcess Integration

#### 7.2.1 YAML ↔ Code Synchronization

**Arquivo:** `src/forgebase/integration/yaml_sync.py`
**Prioridade:** P3
**Complexidade:** Alta

**Descrição:**
Sistema de sincronização bidirecional YAML ↔ Código.

**Responsabilidades:**
- Parse YAML definitions (ForgeProcess)
- Generate code structure from YAML
- Validate code against YAML
- Bidirectional sync

**Features:**
- YAML schema para UseCases
- Code generator
- Validator de consistência
- Diff e sync commands

**Critérios de Aceite:**
- [ ] Parse de YAML funcional
- [ ] Code generation working
- [ ] Validation de consistência
- [ ] Sync bidirecional
- [ ] Docstring explicando filosofia
- [ ] Exemplos de YAML
- [ ] Testes de sync

---

#### 7.2.2 Intent Tracking & Validation

**Arquivo:** `src/forgebase/integration/intent_tracker.py`
**Prioridade:** P3
**Complexidade:** Alta

**Descrição:**
Tracking de intenção original vs execução real.

**Responsabilidades:**
- Captura de intent do ForgeProcess
- Mapeamento intent → execution
- Validação de coerência cognitiva
- Feedback loops

**Critérios de Aceite:**
- [ ] Intent capture funcional
- [ ] Mapeamento automático
- [ ] Validação de coerência
- [ ] Reporting de desvios
- [ ] Docstring explicando conceito
- [ ] Testes de tracking
- [ ] Exemplo de uso

---

## 📚 FASE 8: Documentação & Padrões

**Prioridade:** P1-P3 (Ongoing)
**Dependências:** Paralelo a todas as fases
**Timeline:** Contínuo

### 8.1 Code Documentation

#### 8.1.1 Docstrings reST

**Prioridade:** P1
**Aplicação:** Todos os módulos

**Padrão:**
```python
def method(self, param: str) -> bool:
    """
    [Uma linha descrevendo o que faz]

    [Parágrafo explicando POR QUÊ esta implementação, decisões arquiteturais]

    :param param: Descrição do parâmetro
    :type param: str
    :return: Descrição do retorno
    :rtype: bool
    :raises ExceptionType: Quando ocorre

    Example::

        >>> obj.method("value")
        True
    """
```

**Critérios:**
- [ ] Todas as classes públicas documentadas
- [ ] Todos os métodos públicos documentados
- [ ] Explicação do "porquê", não apenas "o quê"
- [ ] Exemplos de uso incluídos
- [ ] Formato reST validado

---

#### 8.1.2 Architecture Decision Records (ADRs)

**Localização:** `docs/adr/`
**Prioridade:** P1

**ADRs a criar:**
- `001-clean-architecture-choice.md`
- `002-hexagonal-ports-adapters.md`
- `003-observability-first.md`
- `004-cognitive-testing.md`
- `005-dependency-injection.md`
- `006-forgeprocess-integration.md`

**Template ADR:**
```markdown
# ADR-NNN: [Título da Decisão]

## Status
[Aceita | Proposta | Superseded]

## Context
[Contexto e forças que levaram à decisão]

## Decision
[Decisão tomada]

## Consequences
[Consequências positivas e negativas]

## Alternatives Considered
[Alternativas consideradas e por que rejeitadas]
```

---

### 8.2 User Documentation

#### 8.2.1 Getting Started Guide

**Arquivo:** `docs/getting-started.md`
**Prioridade:** P2

**Seções:**
- Instalação
- Primeiro UseCase
- Estrutura de projeto
- Executando exemplos
- Próximos passos

---

#### 8.2.2 API Reference

**Geração:** Sphinx autodoc
**Prioridade:** P2

**Setup:**
- Sphinx configuration
- Theme selection
- Auto-generated from docstrings
- Hosted docs (ReadTheDocs/GitHub Pages)

---

#### 8.2.3 Example Cookbook

**Arquivo:** `docs/cookbook.md`
**Prioridade:** P2

**Receitas:**
- Como criar uma Entity
- Como criar um UseCase
- Como criar um Port
- Como criar um Adapter
- Como instrumentar observabilidade
- Como escrever testes cognitivos
- Como integrar com ForgeProcess

---

### 8.3 Developer Documentation

#### 8.3.1 Contribution Guidelines

**Arquivo:** `CONTRIBUTING.md`
**Prioridade:** P2

**Conteúdo:**
- Code style
- Testing requirements
- PR process
- Commit message format
- Documentation requirements

---

#### 8.3.2 Testing Guide

**Arquivo:** `docs/testing-guide.md`
**Prioridade:** P2

**Conteúdo:**
- Testing philosophy (cognitive tests)
- ForgeTestCase usage
- Fakes vs Mocks
- Coverage requirements
- Performance testing

---

#### 8.3.3 Module Extension Guide

**Arquivo:** `docs/extending-forgebase.md`
**Prioridade:** P2

**Conteúdo:**
- Como adicionar novo Adapter
- Como estender base classes
- Como adicionar observabilidade custom
- Hooks e extension points

---

## 📊 Resumo por Componentes

### Contagem de Componentes

| Tipo | Quantidade | Prioridade Média |
|------|------------|------------------|
| Base Classes | 8 | P0 |
| Domain Components | 4 | P0-P1 |
| Application Components | 4 | P0-P1 |
| Infrastructure | 9 | P1-P2 |
| Observability | 5 | P0-P1 |
| Testing | 6 | P1 |
| Adapters | 3 | P2-P3 |
| Integration | 3 | P2-P3 |
| Documentation | 12 | P1-P3 |
| **TOTAL** | **54** | - |

---

## 🎯 Checklist de Qualidade Global

### Arquitetura
- [ ] Zero dependências circulares
- [ ] Boundaries de Clean Architecture respeitados
- [ ] Ports claramente separados de Adapters
- [ ] Domain isolado de infraestrutura
- [ ] Dependency Injection funcional

### Testes
- [ ] Cobertura ≥90% nos módulos core
- [ ] Testes unitários para todas as base classes
- [ ] Testes de integração para flows completos
- [ ] Testes cognitivos documentando intenção
- [ ] Performance benchmarks

### Observabilidade
- [ ] 100% de UseCases instrumentados
- [ ] 100% de Ports instrumentados
- [ ] Logs estruturados em todos os layers
- [ ] Métricas exportáveis (Prometheus/JSON)
- [ ] Distributed tracing configurável

### Documentação
- [ ] Docstrings reST em todas as classes públicas
- [ ] Exemplos de uso incluídos
- [ ] ADRs documentando decisões
- [ ] Getting started funcional
- [ ] API reference gerado

### Extensibilidade
- [ ] Novos Adapters sem modificar core
- [ ] Novos UseCases seguindo padrão
- [ ] Configuração externalizada
- [ ] Hooks para customização
- [ ] Plugin system (opcional)

### Integrações
- [ ] ForgeProcess YAML sync funcional
- [ ] Intent tracking operacional
- [ ] Feedback loops validados
- [ ] CLI funcional
- [ ] HTTP API funcional

---

## 📅 Roadmap Visual

```
Week 1: Foundation
├─ Day 1-2: Estrutura + Base Classes (Domain, Application)
├─ Day 3-4: Observabilidade Core (LogService, TrackMetrics)
└─ Day 5-7: Infrastructure (Repository, Config, Testing)

Week 2: Adapters & Integration
├─ Day 8-9: CLI Adapter
├─ Day 10-11: HTTP Adapter
└─ Day 12-14: Core Init + Examples

Week 3: Advanced & Polish
├─ Day 15-16: AI/LLM Adapter
├─ Day 17-18: ForgeProcess Integration
└─ Day 19-21: Documentation + Polish

Week 4+: Extensions & Maintenance
└─ Advanced features, community feedback, iterations
```

---

## 🏁 Milestones

### M1: Foundation Complete (Day 7)
**Deliverables:**
- ✅ Todas as base classes implementadas e testadas
- ✅ Estrutura de diretórios completa
- ✅ Observabilidade básica funcional
- ✅ Testes unitários ≥90%

**Criteria:**
- Exemplo simples funciona end-to-end
- CI/CD configurado
- Docs básicas escritas

---

### M2: Adapters & Integration (Day 14)
**Deliverables:**
- ✅ CLI Adapter funcional
- ✅ HTTP Adapter funcional
- ✅ Core initialization working
- ✅ Exemplos completos

**Criteria:**
- Pode executar UseCases via CLI e HTTP
- Métricas visíveis
- Health checks funcionando

---

### M3: Production Ready (Day 21)
**Deliverables:**
- ✅ Todos os adapters implementados
- ✅ ForgeProcess integration
- ✅ Documentação completa
- ✅ Examples & cookbook

**Criteria:**
- Pronto para uso em produção
- Todos os critérios de qualidade atendidos
- Documentação publicada
- Release 1.0.0

---

## 🔄 Processo de Desenvolvimento

### Workflow por Item

1. **Planejamento**
   - Revisar item no backlog
   - Entender dependências
   - Clarificar critérios de aceite

2. **Implementação**
   - Escrever testes primeiro (TDD)
   - Implementar funcionalidade
   - Adicionar observabilidade
   - Escrever docstrings reST

3. **Validação**
   - Rodar testes (≥90% coverage)
   - Verificar sem dependências circulares
   - Validar boundaries arquiteturais
   - Code review

4. **Documentação**
   - Atualizar docs se necessário
   - Adicionar exemplo se aplicável
   - Atualizar ADRs se decisão arquitetural

5. **Integração**
   - Merge para main
   - Atualizar backlog
   - Marcar item como completo

---

## 🎓 Princípios de Implementação

### 1. Reflexividade
> Código que entende e explica seu próprio funcionamento

**Práticas:**
- Docstrings explicando "porquê"
- Métodos `info()` em componentes
- Introspection capabilities
- Self-documentation

### 2. Autonomia
> Módulos independentes com contratos bem definidos

**Práticas:**
- Dependency Injection
- Port/Adapter pattern
- Zero cross-layer dependencies
- Clear interfaces

### 3. Coerência Cognitiva
> Padrões consistentes em toda a arquitetura

**Práticas:**
- Nomenclatura consistente
- Padrões de erro uniformes
- Estrutura modular repetível
- Testes cognitivos validando intenção

---

## 📞 Referências

- **ForgeBase Guide:** `/docs/guides/forgebase_guide.md`
- **ForgeBase PRD:** `/docs/guides/forgebase_PRD.md`
- **Jorge, The Forge:** `/agents/jorge_theforge.md`
- **Bill, Review:** `/agents/bill_review.md`

---

## ✅ Status Tracking

**Última Atualização:** [Data]

**Progresso Geral:**
- [ ] FASE 1: Foundation & Core (0/14 items)
- [ ] FASE 2: Infrastructure (0/9 items)
- [ ] FASE 3: Observability (0/5 items)
- [ ] FASE 4: Testing (0/6 items)
- [ ] FASE 5: Adapters (0/3 items)
- [ ] FASE 6: Core Init (0/1 item)
- [ ] FASE 7: Integration (0/3 items)
- [ ] FASE 8: Documentation (0/12 items)

**Total:** 0/54 items completos (0%)

---

## 📊 KANBAN — Gestão Visual de Desenvolvimento

> Última atualização: 2025-11-03

### Legenda
- 📋 **TODO** — A fazer
- 🔨 **IN PROGRESS** — Em andamento
- 👀 **IN REVIEW** — Em revisão
- ✅ **DONE** — Concluído

---

### 📋 TODO (44)

#### FASE 1: Foundation & Core (0)
*Todos os itens concluídos! ✅*

#### FASE 2: Infrastructure (9)
- [ ] **2.1.1** RepositoryBase (P1)
- [ ] **2.1.2** JSONRepository (P1)
- [ ] **2.1.3** SQLRepository (P2)
- [ ] **2.2.1** ConfigLoader (P1)
- [ ] **2.3.1** LoggerPort (P1)
- [ ] **2.4.1** Sandbox (P2)

#### FASE 3: Observability (5)
- [ ] **3.1.1** LogService (P0)
- [ ] **3.1.2** TrackMetrics (P0)
- [ ] **3.1.3** TracerPort (P1)
- [ ] **3.1.4** FeedbackManager (P1)
- [ ] **3.2.1** @track_metrics Decorator (P1)

#### FASE 4: Testing (6)
- [ ] **4.1.1** ForgeTestCase (P1)
- [ ] **4.2.1** FakeLogger (P1)
- [ ] **4.2.2** FakeRepository (P1)
- [ ] **4.2.3** FakeMetricsCollector (P1)
- [ ] **4.2.4** Sample Data & Fixtures (P1)

#### FASE 5: Adapters (3)
- [ ] **5.1.1** CLIAdapter (P2)
- [ ] **5.2.1** HTTPAdapter (P2)
- [ ] **5.3.1** LLMAdapter (P3)

#### FASE 6: Core Init (1)
- [ ] **6.1.1** core_init.py (P2)

#### FASE 7: Integration (3)
- [ ] **7.1.1** Complete Example Flow (P2)
- [ ] **7.2.1** YAML ↔ Code Sync (P3)
- [ ] **7.2.2** Intent Tracking (P3)

#### FASE 8: Documentation (12)
- [ ] **8.1.1** Docstrings reST (P1) — Ongoing
- [ ] **8.1.2** ADR-001: Clean Architecture (P1)
- [ ] **8.1.2** ADR-002: Hexagonal Ports/Adapters (P1)
- [ ] **8.1.2** ADR-003: Observability First (P1)
- [ ] **8.1.2** ADR-004: Cognitive Testing (P1)
- [ ] **8.1.2** ADR-005: Dependency Injection (P1)
- [ ] **8.1.2** ADR-006: ForgeProcess Integration (P1)
- [ ] **8.2.1** Getting Started Guide (P2)
- [ ] **8.2.2** API Reference (Sphinx) (P2)
- [ ] **8.2.3** Example Cookbook (P2)
- [ ] **8.3.1** CONTRIBUTING.md (P2)
- [ ] **8.3.2** Testing Guide (P2)
- [ ] **8.3.3** Module Extension Guide (P2)

---

### 🔨 IN PROGRESS (0)

*Nenhum item em progresso no momento.*

---

### 👀 IN REVIEW (0)

*Nenhum item em revisão no momento.*

---

### ✅ DONE (10)

#### FASE 1: Foundation & Core (10) ✅
- [x] **1.1** Estrutura de Diretórios (P0)
- [x] **1.2.1** EntityBase (P0) - 17 testes passando
- [x] **1.2.2** ValueObjectBase (P0)
- [x] **1.2.3** Domain Exceptions (P0)
- [x] **1.2.4** Domain Validators (P0)
- [x] **1.3.1** UseCaseBase (P0)
- [x] **1.3.2** PortBase (P0)
- [x] **1.3.3** DTOBase (P1)
- [x] **1.3.4** Error Handling (P1)
- [x] **1.4.1** AdapterBase (P0)

---

## 📈 Métricas de Progresso

| Fase | Total | TODO | In Progress | In Review | Done | % Completo |
|------|-------|------|-------------|-----------|------|------------|
| **FASE 1** | 10 | 0 | 0 | 0 | 10 | 100% ✅ |
| **FASE 2** | 6 | 6 | 0 | 0 | 0 | 0% |
| **FASE 3** | 5 | 5 | 0 | 0 | 0 | 0% |
| **FASE 4** | 5 | 5 | 0 | 0 | 0 | 0% |
| **FASE 5** | 3 | 3 | 0 | 0 | 0 | 0% |
| **FASE 6** | 1 | 1 | 0 | 0 | 0 | 0% |
| **FASE 7** | 3 | 3 | 0 | 0 | 0 | 0% |
| **FASE 8** | 13 | 13 | 0 | 0 | 0 | 0% |
| **TOTAL** | **46** | **36** | **0** | **0** | **10** | **22%** |

---

## 🎯 Próximos Itens Priorizados

**FASE 1 Completa! ✅ Próxima fase:**

**FASE 2 - Infrastructure (P1 - Alto):**

1. 🔨 **2.1.1 RepositoryBase** — Interface abstrata de persistência
2. 🔨 **2.1.2 JSONRepository** — Implementação JSON
3. 🔨 **2.2.1 ConfigLoader** — Gestão de configurações
4. 🔨 **2.3.1 LoggerPort** — Interface de logging

**FASE 3 - Observability (P0-P1 - Crítico/Alto):**

5. ⚡ **3.1.1 LogService** — Logging estruturado
6. ⚡ **3.1.2 TrackMetrics** — Coleta de métricas

---

### 📝 Como Usar Este Kanban

**Mover Item de Coluna:**
1. Marcar como iniciado: Mover de TODO → IN PROGRESS
2. Pronto para revisão: Mover de IN PROGRESS → IN REVIEW
3. Aprovado e completo: Mover de IN REVIEW → DONE

**Atualizar Métricas:**
- Recalcular % completo após cada movimento
- Atualizar tabela de métricas
- Atualizar data de última atualização

**Critérios de "Done":**
- ✅ Código implementado e funcionando
- ✅ Testes escritos (≥90% coverage para core)
- ✅ Docstrings reST completos
- ✅ Code review aprovado
- ✅ CI/CD passando
- ✅ Critérios de aceite atendidos

---

*"Cada linha de código carrega intenção, medição e capacidade de auto-explicação."*

**— Jorge, The Forge**
