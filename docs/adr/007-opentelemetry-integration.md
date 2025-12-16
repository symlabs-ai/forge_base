# ADR-007: OpenTelemetry Integration (Optional)

## Status

**Aceita** (2025-11-05)

## Context

ForgeBase foi projetado com observabilidade nativa desde o início (ver [ADR-003](003-observability-first.md)). Atualmente, o framework possui:

1. **Implementações próprias**:
   - `InMemoryTracer` — tracing para dev/testes
   - `NoOpTracer` — zero overhead em produção
   - `StdoutLogger` — logging estruturado JSON
   - `TrackMetrics` — coleta de métricas in-memory

2. **Abstrações OpenTelemetry-compatible**:
   - `TracerPort` — interface compatível com OTel
   - `LoggerPort` — suporte a structured logging
   - W3C Trace Context format support

3. **Zero dependências obrigatórias** (apenas `pyyaml`)

### Necessidades Emergentes

À medida que ForgeBase é usado em ambientes de produção mais complexos, surgem necessidades:

**1. Integração com Infraestrutura Existente**
- Empresas já usam Jaeger, Zipkin, Prometheus, Grafana
- APMs comerciais (DataDog, New Relic, Dynatrace)
- SIEM systems que esperam formato OTel/OTLP

**2. Auto-Instrumentação**
- Rastrear automaticamente: requests HTTP, queries SQL, chamadas Redis, mensagens Kafka
- Sem necessidade de instrumentar manualmente cada biblioteca

**3. Correlação Automática**
- Correlação automática entre logs, métricas e traces
- Propagação de trace context entre microserviços
- Baggage propagation para contexto cross-service

**4. Exporters Battle-Tested**
- Exporters mantidos pela comunidade para 20+ backends
- Protocolos otimizados (OTLP, gRPC, HTTP/protobuf)
- Retry logic, buffering, batching já implementados

**5. Semantic Conventions**
- Naming consistente seguindo padrões da indústria
- Atributos padronizados (`http.method`, `db.system`, etc.)
- Compatibilidade com ferramentas de análise

### Forças em Jogo

**Necessidades:**
- ✅ Integração com infraestrutura observability existente
- ✅ Auto-instrumentação de bibliotecas populares
- ✅ Exporters para 20+ backends (Jaeger, Prometheus, etc.)
- ✅ Correlação automática logs+metrics+traces
- ✅ Standards da indústria (W3C, OTel semantic conventions)
- ✅ Ecossistema rico e battle-tested

**Riscos:**
- ⚠️ Dependências pesadas (~10+ packages)
- ⚠️ Complexidade de configuração
- ⚠️ Overhead de performance (pequeno mas mensurável)
- ⚠️ Curva de aprendizado
- ⚠️ Vendor lock-in potencial se mal implementado
- ⚠️ Perder simplicidade do "lightweight by default"

**Restrições:**
- 🔒 **Não** pode quebrar filosofia "zero deps obrigatórias"
- 🔒 **Não** pode tornar OTel obrigatório
- 🔒 Sistema cognitivo único (FeedbackManager, IntentTracker) deve ser preservado
- 🔒 Implementações lightweight devem continuar como padrão

## Decision

**Adotamos OpenTelemetry como opção de integração OPCIONAL, não obrigatória.**

### Princípios da Integração

1. **Opt-In, Not Mandatory**
   - OTel é instalado via `pip install forge_base[otel]`
   - Usuário sem OTel: funciona perfeitamente com implementações builtin
   - Usuário com OTel: ativa via configuração

2. **Adapter Pattern**
   - OTel implementa interfaces existentes (`TracerPort`, `LoggerPort`)
   - Não quebra abstrações atuais
   - Intercambiável via configuração

3. **Lightweight by Default**
   - Instalação padrão: zero deps OTel
   - Dev/testes: InMemoryTracer, FakeLogger
   - Produção simples: StdoutLogger, NoOpTracer
   - Produção complexa: OtelTracer, OtelLogger

4. **Preserve Cognitive System**
   - `FeedbackManager` e `IntentTracker` continuam únicos
   - Podem INTEGRAR com OTel (criar spans) mas não são substituídos
   - Sistema cognitivo é diferencial competitivo

### Arquitetura da Integração

```
src/forge_base/observability/
├── tracer_port.py           # Interface abstrata (já existe)
├── logger_port.py           # Interface abstrata (já existe)
├── track_metrics.py         # Implementação builtin (já existe)
│
└── otel/                    # Novo módulo (opcional)
    ├── __init__.py
    ├── otel_tracer.py       # Implementa TracerPort via OTel
    ├── otel_logger.py       # Implementa LoggerPort via OTel
    ├── otel_metrics.py      # Implementa TrackMetrics via OTel
    ├── auto_instrument.py   # Auto-instrumentação de libs
    └── providers.py         # Setup de TracerProvider, etc.
```

### Configuração Declarativa

```yaml
# config-lightweight.yaml (padrão)
observability:
  level: standard

  tracing:
    provider: inmemory     # InMemoryTracer (builtin)

  logging:
    provider: stdout       # StdoutLogger (builtin)

  metrics:
    provider: builtin      # TrackMetrics (builtin)

---

# config-otel.yaml (opcional)
observability:
  level: standard

  tracing:
    provider: opentelemetry
    config:
      service_name: forge_base-api
      exporter: jaeger
      endpoint: http://localhost:14268/api/traces
      sampling_rate: 0.1  # 10%

  logging:
    provider: opentelemetry
    config:
      exporter: otlp
      endpoint: http://localhost:4317

  metrics:
    provider: opentelemetry
    config:
      exporter: prometheus
      endpoint: http://localhost:9090
      interval: 60  # seconds

  # Auto-instrumentação (opcional)
  auto_instrument:
    - requests      # HTTP client
    - sqlalchemy    # Database
    - redis         # Cache
    - flask         # Web framework
```

### Implementação de Adapters

#### OtelTracer (implementa TracerPort)

```python
# src/forge_base/observability/otel/otel_tracer.py

from forge_base.observability.tracer_port import TracerPort, Span, SpanKind, SpanStatus

try:
    from opentelemetry import trace
    from opentelemetry.trace import Status, StatusCode
    HAS_OTEL = True
except ImportError:
    HAS_OTEL = False


class OtelTracer(TracerPort):
    """
    OpenTelemetry implementation of TracerPort.

    This adapter bridges ForgeBase's tracing abstraction with the
    OpenTelemetry SDK, enabling export to any OTel-compatible backend
    (Jaeger, Zipkin, Tempo, DataDog, etc.).

    **Optional dependency**: Install with `pip install forge_base[otel]`

    Why this exists:
    - Enterprises already have OTel infrastructure
    - Auto-instrumentation of popular libraries (requests, sqlalchemy, etc.)
    - Battle-tested exporters for 20+ backends
    - Semantic conventions for consistency

    Design decisions:
    - Lazy import: OTel is optional, not required
    - Adapter pattern: implements TracerPort interface
    - Wraps OTel spans to ForgeBase Span objects

    :param service_name: Name of the service (for grouping)
    :type service_name: str
    :param config: OTel-specific configuration
    :type config: dict

    Example::

        >>> tracer = OtelTracer(service_name="my-api")
        >>> with tracer.span("database_query") as span:
        ...     span.set_attribute("query", "SELECT * FROM users")
        ...     result = db.query()
    """

    def __init__(self, service_name: str, config: Optional[dict] = None):
        if not HAS_OTEL:
            raise ImportError(
                "OpenTelemetry not installed. "
                "Install with: pip install forge_base[otel]"
            )

        self._service_name = service_name
        self._config = config or {}
        self._tracer = trace.get_tracer(service_name)

    def start_span(self, name: str, kind: SpanKind = SpanKind.INTERNAL,
                   **attributes) -> Span:
        """Start a new span using OTel."""
        otel_kind = self._convert_span_kind(kind)
        otel_span = self._tracer.start_span(name, kind=otel_kind)

        # Set attributes
        for key, value in attributes.items():
            otel_span.set_attribute(key, value)

        # Wrap OTel span in ForgeBase Span
        return self._wrap_otel_span(otel_span)

    def _wrap_otel_span(self, otel_span) -> Span:
        """Wrap OTel span to ForgeBase Span interface."""
        ctx = otel_span.get_span_context()

        return Span(
            span_id=format(ctx.span_id, '016x'),
            trace_id=format(ctx.trace_id, '032x'),
            name=otel_span.name,
            kind=self._convert_span_kind_back(otel_span.kind),
            # ... bridge other fields
        )

    # ... implementation details
```

#### Auto-Instrumentation

```python
# src/forge_base/observability/otel/auto_instrument.py

def auto_instrument(config: dict) -> None:
    """
    Auto-instrument popular libraries for automatic tracing.

    This function activates OpenTelemetry instrumentation for common
    Python libraries, enabling automatic span creation without manual
    instrumentation.

    Supported libraries:
    - requests, httpx, aiohttp (HTTP clients)
    - flask, fastapi, django (web frameworks)
    - sqlalchemy, psycopg2, pymysql (databases)
    - redis, celery (async/messaging)
    - boto3 (AWS SDK)

    Why this is valuable:
    - Zero code changes needed
    - Consistent instrumentation
    - Community-maintained

    :param config: Dict with library names as keys, True to enable
    :type config: dict

    Example::

        >>> auto_instrument({
        ...     "requests": True,
        ...     "sqlalchemy": True,
        ...     "redis": True
        ... })
    """

    if config.get("requests"):
        from opentelemetry.instrumentation.requests import RequestsInstrumentor
        RequestsInstrumentor().instrument()

    if config.get("sqlalchemy"):
        from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
        SQLAlchemyInstrumentor().instrument()

    if config.get("redis"):
        from opentelemetry.instrumentation.redis import RedisInstrumentor
        RedisInstrumentor().instrument()

    if config.get("flask"):
        from opentelemetry.instrumentation.flask import FlaskInstrumentor
        FlaskInstrumentor().instrument()

    # ... more instrumentations
```

### Integração com Sistema Cognitivo

FeedbackManager e IntentTracker **integram** com OTel mas não são substituídos:

```python
# src/forge_base/observability/feedback_manager.py

class FeedbackManager:
    def __init__(self, tracer: TracerPort):
        self._tracer = tracer  # Pode ser OtelTracer ou InMemoryTracer

    def capture_intent(self, description: str, **context):
        """Capture intent and create trace span."""

        # Create span (works with any TracerPort implementation)
        with self._tracer.span("cognitive.capture_intent") as span:
            span.set_attribute("intent.description", description)
            span.set_attribute("intent.source", "forgeprocess")

            # Lógica cognitiva única do ForgeBase
            intent_record = self._create_intent_record(description, context)

            # If using OTel, this span will be exported to Jaeger/etc
            # If using InMemory, it stays in memory for tests

            return intent_record
```

**Diferencial:** Sistema cognitivo cria spans especiais com semântica única:
- `cognitive.capture_intent`
- `cognitive.validate_coherence`
- `cognitive.feedback_loop`

Estes não existem no OTel padrão — são inovação do ForgeBase.

### Instalação e Setup

#### Instalação Padrão (Lightweight)
```bash
# Zero OTel dependencies
pip install forge_base
```

#### Instalação com OTel
```bash
# OTel SDK only
pip install forge_base[otel]

# OTel + common exporters
pip install forge_base[otel-exporters]

# OTel + auto-instrumentation
pip install forge_base[otel-auto]

# Everything
pip install forge_base[all]
```

#### pyproject.toml
```toml
[project.optional-dependencies]
# OpenTelemetry support (optional)
otel = [
    "opentelemetry-api>=1.20.0",
    "opentelemetry-sdk>=1.20.0",
]

# Common exporters
otel-exporters = [
    "forge_base[otel]",
    "opentelemetry-exporter-jaeger>=1.20.0",
    "opentelemetry-exporter-prometheus>=0.41b0",
    "opentelemetry-exporter-otlp>=1.20.0",
]

# Auto-instrumentation for popular libraries
otel-auto = [
    "forge_base[otel]",
    "opentelemetry-instrumentation-requests>=0.41b0",
    "opentelemetry-instrumentation-flask>=0.41b0",
    "opentelemetry-instrumentation-sqlalchemy>=0.41b0",
    "opentelemetry-instrumentation-redis>=0.41b0",
]

# All optional features
all = [
    "forge_base[dev,sql,otel,otel-exporters,otel-auto]",
]
```

## Consequences

### Positivas

✅ **Integração Enterprise-Ready**
- Conecta com infraestrutura observability existente
- Suporta Jaeger, Zipkin, Prometheus, Grafana, APMs comerciais
- OTLP protocol para interoperabilidade

✅ **Auto-Instrumentação Zero-Code**
```python
# Antes: instrumentar manualmente
span = tracer.start_span("http_request")
response = requests.get(url)
span.end()

# Depois (com OTel auto-instrument): automático!
response = requests.get(url)  # Span criado automaticamente
```

✅ **Correlação Automática**
```json
{
  "timestamp": "2025-11-05T10:30:00Z",
  "message": "User created",
  "trace_id": "abc123",        // ← Correlação automática
  "span_id": "def456",
  "service.name": "forge_base-api",
  "usecase.name": "CreateUser"
}
```

✅ **Semantic Conventions**
- Naming consistente seguindo padrões OTel
- Atributos padronizados reconhecidos por ferramentas
- Melhor análise e queries

✅ **Battle-Tested Exporters**
- Mantidos pela comunidade CNCF
- Otimizados (batching, compression, retry)
- Produção-ready

✅ **Ecosystem Rico**
- Instrumentação para 100+ bibliotecas
- Integração com APMs comerciais
- Ferramentas de análise e visualização

✅ **Mantém Filosofia Original**
- Zero deps obrigatórias ✅
- Lightweight by default ✅
- Opt-in, não mandatory ✅
- Sistema cognitivo preservado ✅

### Negativas

⚠️ **Dependências Pesadas (quando ativado)**
```bash
# OTel SDK + exporters + instrumentations
~15-20 packages adicionais
~50MB de dependências
```
**Mitigation:** Opcional, não instalado por padrão

⚠️ **Complexidade de Setup**
```python
# Setup OTel não é trivial
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter

provider = TracerProvider()
processor = BatchSpanProcessor(JaegerExporter(...))
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)
```
**Mitigation:** ForgeBase abstrai setup via configuração YAML

⚠️ **Overhead de Performance**
- ~1-5ms por span
- Memória para buffering
- CPU para serialização

**Mitigation:**
- Sampling configurável (ex: 10% de requests)
- Batch processing
- Async exporters

⚠️ **Curva de Aprendizado**
- Conceitos: Providers, Exporters, Processors, Context, Baggage
- Configuração de exporters
- Debugging de problemas OTel

**Mitigation:**
- Documentação clara
- Exemplos práticos
- Defaults sensatos

⚠️ **Manutenção de Adapter**
- Precisa acompanhar updates OTel API
- Mapear conceitos ForgeBase ↔ OTel
- Testes de compatibilidade

**Mitigation:**
- Tests automatizados
- CI/CD para verificar compatibilidade
- Versionamento semântico

### Neutras

📊 **Escolha de Backend**
- Usuário decide: Jaeger, Prometheus, DataDog, etc.
- ForgeBase não opina sobre backend
- Configuração por arquivo YAML

📊 **Coexistência de Implementações**
- Builtin e OTel coexistem
- Escolha por ambiente (dev vs prod)
- Transição gradual possível

## Alternatives Considered

### 1. OTel Obrigatório (Rejected ❌)

**Abordagem:** Tornar OTel dependência obrigatória.

```toml
dependencies = [
    "pyyaml>=6.0",
    "opentelemetry-api>=1.20.0",  # ← Obrigatório
    "opentelemetry-sdk>=1.20.0",
]
```

**Rejeitado porque:**
- ❌ Quebra filosofia "lightweight by default"
- ❌ Força usuários simples a carregar 50MB+ deps
- ❌ Contra princípio "zero deps obrigatórias"
- ❌ Overkill para uso local/dev/testes
- ❌ Vendor lock-in (mesmo que open source)

### 2. Substituir Implementações Builtin (Rejected ❌)

**Abordagem:** Remover InMemoryTracer, StdoutLogger; usar apenas OTel.

**Rejeitado porque:**
- ❌ Perde simplicidade para casos básicos
- ❌ Testes ficam mais lentos (setup OTel)
- ❌ Dev experience degrada (precisa subir Jaeger local)
- ❌ Contra princípio de autonomia

### 3. Fork OTel (Rejected ❌)

**Abordagem:** Criar fork do OTel customizado para ForgeBase.

**Rejeitado porque:**
- ❌ Manutenção pesada
- ❌ Perde updates da comunidade
- ❌ Fragmenta ecossistema
- ❌ Reinventando a roda

### 4. Apenas Protocolo OTLP (Considered, but insufficient)

**Abordagem:** Suportar apenas export via OTLP protocol, sem OTel SDK.

```python
# Exportar spans no formato OTLP sem SDK
def export_otlp(spans: List[Span]):
    payload = serialize_to_otlp(spans)
    requests.post("http://collector:4318/v1/traces", json=payload)
```

**Parcialmente rejeitado porque:**
- ✅ Leve (zero deps OTel)
- ❌ Perde auto-instrumentação
- ❌ Perde context propagation automática
- ❌ Perde semantic conventions helpers
- ❌ Perde ecosystem de instrumentations

**Decisão:** Usar este approach para implementações builtin (export OTLP direto), mas também oferecer OTel completo como opção.

### 5. Abordagem Híbrida (Accepted ✅)

**Nossa decisão:**
- ✅ Builtin implementations (lightweight, padrão)
- ✅ OTel adapter (opcional, enterprise)
- ✅ OTLP export direto (builtin, sem deps)
- ✅ Configuração declarativa
- ✅ Preserva sistema cognitivo único

**Melhor dos mundos:**
- Simples quando não precisa
- Poderoso quando precisa
- Transição gradual possível

## Implementation Notes

### Fase 1: Fundação (Dias 1-2)

```bash
# Criar estrutura de módulo OTel
src/forge_base/observability/otel/
├── __init__.py
├── otel_tracer.py      # Implementa TracerPort
├── otel_logger.py      # Implementa LoggerPort
├── otel_metrics.py     # Implementa TrackMetrics
├── providers.py        # Setup de providers
└── auto_instrument.py  # Auto-instrumentation
```

**Critérios de aceite:**
- [ ] OtelTracer implementa TracerPort completamente
- [ ] Lazy import (funciona sem OTel instalado)
- [ ] Docstrings explicando uso
- [ ] Tests com OTel mock

### Fase 2: Configuração (Dia 3)

```yaml
# Adicionar ao config schema
observability:
  tracing:
    provider: opentelemetry | inmemory | noop
    config:
      service_name: str
      exporter: jaeger | zipkin | otlp
      endpoint: str
      sampling_rate: float
```

**Critérios de aceite:**
- [ ] ConfigLoader valida schema OTel
- [ ] Bootstrap cria OtelTracer se configurado
- [ ] Fallback para InMemory se OTel não instalado
- [ ] Erro claro se config incompleta

### Fase 3: Auto-Instrumentation (Dias 4-5)

```python
# Implementar auto-instrumentation
auto_instrument({
    "requests": True,
    "flask": True,
    "sqlalchemy": True
})
```

**Critérios de aceite:**
- [ ] Suporte para 5+ bibliotecas populares
- [ ] Documentação de quais libraries suportadas
- [ ] Tests com instrumentação ativa
- [ ] Performance benchmarks

### Fase 4: Integração Sistema Cognitivo (Dia 6)

```python
# FeedbackManager integra com OTel
feedback = FeedbackManager(tracer=OtelTracer())
```

**Critérios de aceite:**
- [ ] FeedbackManager funciona com OtelTracer
- [ ] IntentTracker funciona com OtelTracer
- [ ] Spans cognitivos aparecem em Jaeger
- [ ] Attributes customizados preservados

### Fase 5: Exemplos e Docs (Dia 7)

```markdown
# docs/otel-integration.md
- When to use OTel vs builtin
- How to configure exporters
- How to enable auto-instrumentation
- Performance considerations
- Troubleshooting common issues
```

**Critérios de aceite:**
- [ ] Exemplo completo end-to-end
- [ ] Documentação clara
- [ ] Screenshots de Jaeger/Prometheus
- [ ] Troubleshooting guide

### Fase 6: Testing (Dia 8)

```python
# tests/integration/test_otel_integration.py
def test_otel_tracer_compatibility():
    """Verify OtelTracer implements TracerPort."""

def test_auto_instrumentation():
    """Verify auto-instrumentation creates spans."""

def test_exporter_integration():
    """Verify export to Jaeger works."""
```

**Critérios de aceite:**
- [ ] Tests de compatibilidade TracerPort
- [ ] Tests de auto-instrumentation
- [ ] Tests de exporters (mock)
- [ ] Coverage ≥80%

### Timeline Estimado

| Fase | Dias | Complexidade |
|------|------|--------------|
| 1. Fundação | 2 | Alta |
| 2. Configuração | 1 | Média |
| 3. Auto-Instrumentation | 2 | Alta |
| 4. Integração Cognitiva | 1 | Média |
| 5. Exemplos e Docs | 1 | Baixa |
| 6. Testing | 1 | Média |
| **Total** | **8 dias** | - |

### Risks & Mitigations

| Risco | Impacto | Probabilidade | Mitigation |
|-------|---------|---------------|------------|
| Breaking changes OTel API | Alto | Baixa | Pin versions, CI tests |
| Performance overhead alto | Médio | Média | Benchmarks, sampling |
| Complexidade assusta users | Médio | Alta | Docs claras, defaults sensatos |
| Manutenção de adapter | Médio | Média | Tests, semantic versioning |
| Bugs em instrumentations | Baixo | Média | Community mantém, reportar upstream |

## References

### OpenTelemetry

- **OpenTelemetry Website:** https://opentelemetry.io/
- **OTel Python SDK:** https://github.com/open-telemetry/opentelemetry-python
- **Semantic Conventions:** https://opentelemetry.io/docs/concepts/semantic-conventions/
- **W3C Trace Context:** https://www.w3.org/TR/trace-context/

### Distributed Tracing

- **Distributed Tracing in Practice** by Austin Parker et al.
- **Jaeger Documentation:** https://www.jaegertracing.io/docs/
- **Zipkin Documentation:** https://zipkin.io/

### ForgeBase Related

- **ADR-003: Observability First** — Filosofia de observabilidade nativa
- **TracerPort Implementation** — `src/forge_base/observability/tracer_port.py`
- **FeedbackManager** — Sistema cognitivo único

## Related ADRs

- [ADR-003: Observability First](003-observability-first.md) — Base filosófica
- [ADR-001: Clean Architecture Choice](001-clean-architecture-choice.md) — Boundaries
- [ADR-002: Hexagonal Ports-Adapters](002-hexagonal-ports-adapters.md) — Adapter pattern
- [ADR-005: Dependency Injection](005-dependency-injection.md) — DI container
- [ADR-006: ForgeProcess Integration](006-forgeprocess-integration.md) — Sistema cognitivo

---

**Author:** ForgeBase Development Team
**Date:** 2025-11-05
**Version:** 1.0
**Status:** Aceita para implementação

---

## Appendix A: Comparison Matrix

| Feature | Builtin (InMemory) | OTel Integration |
|---------|-------------------|------------------|
| **Dependencies** | Zero | ~15 packages |
| **Setup Complexity** | Trivial | Medium |
| **Auto-Instrumentation** | ❌ Manual | ✅ Automático |
| **Exporters** | JSON, Memory | 20+ backends |
| **Context Propagation** | Basic | W3C standard |
| **Semantic Conventions** | Custom | OTel standard |
| **Performance Overhead** | ~0.1ms | ~1-5ms |
| **Production Ready** | ✅ Simple cases | ✅ Enterprise |
| **Ecosystem** | ForgeBase only | CNCF ecosystem |
| **Learning Curve** | Low | Medium |
| **Use Case** | Dev, tests, simple prod | Complex prod, microservices |

## Appendix B: Example Configurations

### Local Development
```yaml
observability:
  tracing:
    provider: inmemory  # Lightweight, fast
  logging:
    provider: stdout    # Console output
  metrics:
    provider: builtin   # In-memory
```

### Staging with Jaeger
```yaml
observability:
  tracing:
    provider: opentelemetry
    config:
      service_name: forge_base-staging
      exporter: jaeger
      endpoint: http://jaeger:14268/api/traces
      sampling_rate: 0.5  # 50%

  auto_instrument:
    - requests
    - sqlalchemy
```

### Production with Full Stack
```yaml
observability:
  tracing:
    provider: opentelemetry
    config:
      service_name: forge_base-prod
      exporter: otlp
      endpoint: http://otel-collector:4317
      sampling_rate: 0.1  # 10% (high traffic)

  logging:
    provider: opentelemetry
    config:
      exporter: otlp
      endpoint: http://otel-collector:4317

  metrics:
    provider: opentelemetry
    config:
      exporter: prometheus
      endpoint: http://prometheus:9090
      interval: 60

  auto_instrument:
    - requests
    - flask
    - sqlalchemy
    - redis
    - celery
```

## Appendix C: Migration Path

### Para usuários atuais do ForgeBase

**Step 1: Continue usando builtin (nada muda)**
```bash
# Seu código continua funcionando
pip install forge_base==0.1.4
```

**Step 2: Experimente OTel localmente**
```bash
pip install forge_base[otel]
# Update config.yaml para usar OTel
# Suba Jaeger local: docker run -p 16686:16686 jaegertracing/all-in-one
```

**Step 3: Deploy gradual em staging**
```yaml
# Staging: 10% de traces via OTel, resto builtin
observability:
  tracing:
    provider: opentelemetry
    config:
      sampling_rate: 0.1
```

**Step 4: Rollout production**
```yaml
# Production: OTel full
observability:
  tracing:
    provider: opentelemetry
```

**Rollback é trivial:** Mudar `provider: opentelemetry` → `provider: inmemory` no config.

---

*"Observabilidade não é uma camada adicional, mas uma propriedade intrínseca do código cognitivo."*

**— Jorge, The Forge**
