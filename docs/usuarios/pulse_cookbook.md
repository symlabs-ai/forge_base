# ForgePulse — Cookbook

Referencia completa com receitas para cada feature do ForgePulse.
Cada secao contem explicacao breve e snippet executavel.

> Pre-requisito: leia o [Quick Start](pulse_quick_start.md) primeiro.

---

## Sumario

1. [Monitoring Levels](#1-monitoring-levels)
2. [Hierarquia de mapeamento](#2-hierarquia-de-mapeamento)
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
13. [Testando com FakeMetricsCollector](#13-testando-com-fakemetricscollector)
14. [Referencia rapida](#14-referencia-rapida)

---

## 1. Monitoring Levels

`MonitoringLevel` e um `IntEnum` que controla a granularidade da coleta.
Niveis mais altos incluem tudo dos anteriores.

| Level | Valor | Labels emitidas | Campos extras no ExecutionRecord |
|-------|-------|-----------------|----------------------------------|
| OFF | 0 | nenhuma (zero overhead) | — |
| BASIC | 10 | `use_case`, `value_track` | spans |
| STANDARD | 20 | + `subtrack` | spans |
| DETAILED | 30 | + `feature` | spans, tags, attributes em spans |
| DIAGNOSTIC | 40 | + `feature` | spans, tags, extra, mapping_source, dropped_spans, start_ns/end_ns em spans |

```python
from forge_base.pulse import MonitoringLevel

# Comparacao direta (IntEnum)
assert MonitoringLevel.DETAILED >= MonitoringLevel.STANDARD

# OFF: runner chama execute() direto, sem instrumentacao
# BASIC: metricas com {use_case, value_track}
# STANDARD: adiciona {subtrack} nas labels
# DETAILED: adiciona {feature}, salva tags e span attributes
# DIAGNOSTIC: inclui extra, mapping_source, dropped_spans, timestamps de spans
```

### Exemplo: escolhendo o level

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

# STANDARD: labels incluem subtrack
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

## 2. Hierarquia de mapeamento

O runner resolve contexto (value_track, subtrack, feature) em 4 camadas,
cada uma podendo sobrescrever a anterior:

| Prioridade | Fonte | mapping_source |
|------------|-------|----------------|
| 1 (base) | Heuristic (modulo/classe) | `"heuristic"` |
| 2 | `@pulse_meta` decorator | `"decorator"` |
| 3 | `ValueTrackRegistry` (YAML) | `"spec"` |
| 4 (topo) | `ctx_overrides` em `run()` | valor passado |

```python
from forge_base.pulse import (
    BasicCollector, MonitoringLevel, UseCaseRunner,
    pulse_meta, ValueTrackRegistry,
)
from forge_base.testing.fakes import FakeMetricsCollector

# Camada 1: heuristic extrai use_case_name da classe, feature do modulo
# Camada 2: @pulse_meta sobrescreve subtrack, feature, value_track
# Camada 3: registry.resolve() sobrescreve se encontrar no YAML
# Camada 4: runner.run(input, value_track="override") sobrescreve tudo

metrics = FakeMetricsCollector()
collector = BasicCollector(metrics=metrics, level=MonitoringLevel.BASIC)
runner = UseCaseRunner(
    use_case=PingUseCase(),
    level=MonitoringLevel.BASIC,
    collector=collector,
)

# Override no run(): camada 4 sobrescreve tudo
runner.run(PingInput(), value_track="checkout", subtrack="payment")
```

### Visualizando o mapping_source

Com `DIAGNOSTIC`, o snapshot inclui `mapping_source` em cada execucao:

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

Decorator de classe que define metadados estaticos de observabilidade.
Nao altera a execucao — apenas registra informacao.

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

### Parametros

| Parametro | Tipo | Default | Descricao |
|-----------|------|---------|-----------|
| `subtrack` | `str` | `""` | Sobrescreve subtrack heuristico |
| `feature` | `str` | `""` | Sobrescreve feature heuristica |
| `value_track` | `str` | `""` | Sobrescreve value_track (default `"legacy"`) |
| `tags` | `dict[str, str]` | `None` | Tags estaticas, congeladas em `MappingProxyType` |

### Lendo metadata programaticamente

```python
meta = read_pulse_meta(GenerateInvoiceUseCase)
if meta:
    print(meta.subtrack)     # "billing"
    print(meta.value_track)  # "checkout"
    print(dict(meta.tags))   # {"team": "payments", "tier": "critical"}
```

---

## 4. ValueTrackRegistry (YAML)

Mapeamento centralizado de UseCases para value tracks via YAML.
Prioridade maior que `@pulse_meta`, menor que overrides em `run()`.

### Schema spec 0.1

```yaml
schema_version: "0.1"

value_tracks:
  checkout:
    description: "Fluxo de compra"
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

**Regras do schema:**

- `schema_version`: obrigatorio, apenas `"0.1"` suportado
- `value_tracks`: dict nao-vazio
- Cada track precisa de `usecases` (lista nao-vazia, sem duplicatas)
- `subtracks`: opcional, cada UC deve existir na lista `usecases` da track
- `tags`: opcional, `dict[str, str]`
- `description`: opcional

### Carregando e usando

```python
from pathlib import Path
from forge_base.pulse import ValueTrackRegistry

registry = ValueTrackRegistry()
registry.load_from_yaml(Path("pulse_spec.yaml"))

# Resolve por nome de classe
mapping = registry.resolve("GenerateInvoiceUseCase")
if mapping:
    print(mapping.value_track)    # "checkout"
    print(mapping.subtrack)       # "billing"
    print(mapping.mapping_source) # "spec"
    print(dict(mapping.tags))     # {"domain": "commerce"}
```

### Carregando de dict (sem arquivo)

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

### Integrando com UseCaseRunner

```python
runner = UseCaseRunner(
    use_case=GenerateInvoiceUseCase(),
    level=MonitoringLevel.STANDARD,
    collector=collector,
    registry=registry,
)
# O runner chama registry.resolve() automaticamente em cada run()
```

---

## 5. Tags

Tags sao pares chave-valor que enriquecem o contexto de execucao.
Duas fontes sao mescladas pelo runner:

| Prioridade | Fonte | Quando |
|------------|-------|--------|
| 1 (base) | `@pulse_meta(tags={...})` | Init do runner |
| 2 (topo) | `runner.run(..., tags={...})` | Cada chamada |

Runtime tags sobrescrevem decorator tags em caso de conflito de chave.

> **Nota:** Tags definidas no YAML spec ficam disponiveis no objeto
> `ValueTrackMapping` (via `mapping.tags`), mas **nao** sao mescladas
> automaticamente no `ExecutionContext.tags` pelo runner.

### Level gating

Tags so aparecem no `ExecutionRecord` e no snapshot a partir de
`DETAILED` (30). Em niveis inferiores as tags sao ignoradas na saida.

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

# Runtime tags mesclam com decorator tags
runner.run(PingInput(), tags={"env": "staging", "team": "checkout"})

snapshot = collector.snapshot()
tags = snapshot.executions[0]["tags"]
print(dict(tags))
# {"team": "checkout", "env": "staging"}
# "team" veio do runtime, sobrescrevendo o decorator
```

---

## 6. pulse_span

Context manager para medir trechos internos do `execute()`.
Cria `SpanRecord` com duracao, suporta nesting e atributos.

### Basico

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
            pass  # validacao

        with pulse_span("charge_payment", provider="stripe"):
            pass  # cobranca

        return PingOutput()
```

### No-op fora do runner

```python
# Chamar pulse_span fora de um UseCaseRunner ativo e seguro:
# yield None, zero overhead
with pulse_span("noop") as span:
    assert span is None
```

### Nesting (parent-child)

Spans aninhados recebem `parent_span_id` automaticamente:

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

### Atributos em spans

Kwargs passados a `pulse_span` viram `attributes` no SpanRecord.
Visiveis no snapshot apenas a partir de `DETAILED`:

```python
with pulse_span("http_call", method="POST", url="/api/charge"):
    pass  # chamada HTTP

# No snapshot com DETAILED+:
# {"name": "http_call", "attributes": {"method": "POST", "url": "/api/charge"}, ...}
```

### Timestamps (DIAGNOSTIC)

Em `DIAGNOSTIC`, spans incluem `start_ns` e `end_ns` (nanosegundos):

```python
# Com DIAGNOSTIC:
# {"name": "http_call", "start_ns": 123456789, "end_ns": 123457000, ...}
```

---

## 7. BudgetPolicy

Limita a quantidade de spans por execucao, evitando explosao de dados
em UseCases com muitas iteracoes.

```python
from forge_base.pulse import BudgetPolicy

budget = BudgetPolicy(
    max_spans_per_execution=10,   # maximo 10 spans (default: 64)
    max_events_per_execution=128, # reservado para uso futuro
)
```

### Uso com runner

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
print(record["dropped_spans"])  # 45 (visivel em DIAGNOSTIC)
```

Quando o budget e atingido, `pulse_span` retorna `None` (no-op) — nao
lanca excecao.

---

## 8. SamplingPolicy

Controla a taxa de amostragem para reduzir volume de dados.
Tres niveis de especificidade:

```python
from forge_base.pulse import SamplingPolicy

policy = SamplingPolicy(
    default_rate=0.5,  # 50% de todas as execucoes
    by_value_track={"checkout": 1.0, "analytics": 0.1},
    by_tenant={"tenant_vip": 1.0},
)
```

### Resolucao (mais especifico vence)

1. `by_tenant` — verifica `ctx.extra["tenant"]`
2. `by_value_track` — verifica `ctx.value_track`
3. `default_rate` — fallback

```python
# Todas as execucoes do checkout sao amostradas (1.0)
# Tenant VIP sempre amostrado independente do track
# Demais: 50% de chance

metrics = FakeMetricsCollector()
collector = BasicCollector(metrics=metrics, level=MonitoringLevel.BASIC)
runner = UseCaseRunner(
    use_case=PingUseCase(),
    level=MonitoringLevel.BASIC,
    collector=collector,
    policy=policy,
)
```

### Usando tenant no sampling

Para que `by_tenant` funcione, passe `tenant` via `extra` no `run()`.
O dict `extra` passa por `redact_keys` automaticamente — evite chaves
com nomes sensiveis (como `api_key`) se precisar le-las depois.

```python
runner.run(PingInput(), extra={"tenant": "tenant_vip"})
```

### Rates validos

- `1.0` — sempre amostrado
- `0.0` — nunca amostrado (metricas basicas ainda emitidas)
- `0.0 < rate < 1.0` — probabilistico (`random.random() < rate`)

---

## 9. ExportPipeline

Pipeline assincrono para exportar `ExecutionRecord` via buffer + exporter.

### Componentes

| Classe | Papel |
|--------|-------|
| `AsyncBuffer` | Fila thread-safe com politica de drop |
| `JsonLinesExporter` | Escreve JSON Lines em stream |
| `InMemoryExporter` | Armazena tuplas `(context, data)` em lista |
| `ExportPipeline` | Orquestra buffer + exporter via `flush()` |

### AsyncBuffer

```python
from forge_base.pulse import AsyncBuffer

buffer = AsyncBuffer(
    max_size=10_000,       # capacidade (default: 10_000)
    drop_policy="oldest",  # "oldest" (evict) ou "newest" (reject)
)

# Push e sincrono (usado pelo collector)
# buffer.push(record) -> bool

print(buffer.size)        # itens no buffer
print(buffer.drop_count)  # total de drops desde criacao
```

### JsonLinesExporter

Escreve cada record como uma linha JSON compacta:

```python
import io
from forge_base.pulse import JsonLinesExporter

stream = io.StringIO()
exporter = JsonLinesExporter(stream=stream)

# Apos flush:
# stream.getvalue() contem linhas JSON separadas por \n
```

### InMemoryExporter

Util para testes — armazena records na memoria:

```python
from forge_base.pulse import InMemoryExporter

exporter = InMemoryExporter()

# Apos flush:
for ctx, data in exporter.records:
    print(data["use_case_name"], data["duration_ms"])
```

### Pipeline completo

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

# Executa algumas vezes
for _ in range(5):
    runner.run(PingInput())

# Monta pipeline
stream = io.StringIO()
buffer = AsyncBuffer(max_size=1000)
pipeline = ExportPipeline(buffer=buffer, exporter=JsonLinesExporter(stream=stream))

# Transfere records para o buffer
# Nota: _records e atributo interno do BasicCollector.
# Em producao, conecte o buffer diretamente ao collector
# ou use um collector customizado que faca push no buffer.
for record in collector._records:
    buffer.push(record)

# Flush assincrono
async def export():
    count = await pipeline.flush()
    print(f"Exportados: {count} records")
    print(stream.getvalue()[:200])

asyncio.run(export())
```

---

## 10. DashboardSummary

Agrega dados de um `PulseSnapshot` em metricas de dashboard:
total de execucoes, taxa de erro, duracao media, p95, top error types.

```python
from forge_base.pulse import DashboardSummary

snapshot = collector.snapshot()
summary = DashboardSummary.from_snapshot(snapshot, top_n=5)

print(f"Total: {summary.total_executions}")
print(f"Sucesso: {summary.successful}")
print(f"Falhas: {summary.failed}")
print(f"Error rate: {summary.error_rate:.2%}")
print(f"Duracao media: {summary.mean_duration_ms:.2f}ms")
print(f"Top erros: {summary.top_error_types}")
```

### TrackSummary (por value track)

```python
for track in summary.by_value_track:
    print(
        f"  {track.value_track}: "
        f"{track.total_executions} exec, "
        f"p95={track.p95_duration_ms:.2f}ms, "
        f"err={track.error_rate:.2%}"
    )
```

### Estrutura completa

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

`ExtensionCompatibilityMatrix` valida se extensoes de terceiros sao
compativeis com a versao atual do ForgePulse.

```python
from forge_base.pulse import ExtensionCompatibilityMatrix, PULSE_SCHEMA_VERSION

ecm = ExtensionCompatibilityMatrix()

# Registra extensoes com a versao minima de ForgePulse que exigem
ecm.register_extension(
    name="forge-otel-bridge",
    version="1.2.0",
    requires_pulse="0.3",
)
ecm.register_extension(
    name="forge-sentry",
    version="2.0.0",
    requires_pulse="0.4",  # versao futura
)
```

### Validacao

```python
# Lista incompativeis
issues = ecm.validate(PULSE_SCHEMA_VERSION)
for issue in issues:
    print(f"{issue.name} v{issue.version}: requer pulse {issue.requires_pulse}, atual {issue.actual_pulse}")

# Raise se houver incompatibilidade
from forge_base.pulse import PulseIncompatibleExtensionError
try:
    ecm.validate_or_raise(PULSE_SCHEMA_VERSION)
except PulseIncompatibleExtensionError as e:
    print(e)

# Warning (nao bloqueia)
issues = ecm.validate_or_warn(PULSE_SCHEMA_VERSION)
```

### Regras de compatibilidade

- Major deve ser igual
- Minor do pulse deve ser `>=` o requerido pela extensao
- Formatos aceitos: `"major.minor"` ou `"major.minor.patch"`

---

## 12. Redaction

`redact_keys` substitui valores de chaves sensiveis por `"[REDACTED]"`.
Chamada automaticamente por `ExecutionContext.build()` no dict `extra`.

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

### Padroes detectados

| Padrao | Exemplo de match |
|--------|-----------------|
| `password` | `password`, `user_password` |
| `secret` | `client_secret` |
| `token` | `access_token` |
| `api_key` / `api-key` | `api_key`, `api-key` |
| `auth_token` / `auth_key` / `auth_secret` / `auth_header` / `auth_cookie` / `auth_code` / `auth_hash` | `auth_token` |
| `credential` | `db_credential` |
| `private_key` / `private-key` | `private_key` |
| `ssn` | `ssn`, `user_ssn` |
| `credit_card` / `credit-card` | `credit_card` |

A deteccao e case-insensitive.

---

## 13. Testando com FakeMetricsCollector

`FakeMetricsCollector` e um coletor in-memory para testes.
Satisfaz `PulseMetricsProtocol`.

```python
from forge_base.testing.fakes import FakeMetricsCollector

metrics = FakeMetricsCollector()
```

### Assertions integradas

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

# Verificar se contador foi incrementado
assert metrics.was_incremented("pulse.execution.count")

# Verificar valor exato
metrics.assert_counter_equals(
    "pulse.execution.count",
    1,
    use_case="PingUseCase",
    value_track="legacy",
)

# Verificar que duracao foi registrada
assert metrics.was_recorded("pulse.execution.duration_ms")

# Acessar valores diretamente
count = metrics.get_counter(
    "pulse.execution.count",
    use_case="PingUseCase",
    value_track="legacy",
)
assert count == 1

# Verificar que contador e maior que N
metrics.assert_counter_greater(
    "pulse.execution.count",
    0,
    use_case="PingUseCase",
    value_track="legacy",
)
```

### Report completo

```python
report = metrics.report()
print(report["counters"])     # {"pulse.execution.count{...}": 1, ...}
print(report["gauges"])       # {}
print(report["histograms"])   # {"pulse.execution.duration_ms{...}": {"count": 1, ...}}
```

### SpyCollector pattern

Para testes que precisam capturar as chamadas do collector:

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

### Reset entre testes

```python
metrics.clear()   # limpa todos os contadores, gauges, histograms
metrics.reset()   # alias de clear()
collector.clear_records()  # limpa records do BasicCollector
```

---

## 14. Referencia rapida

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

| O que voce quer | Como fazer |
|-----------------|------------|
| Monitorar um UseCase | `UseCaseRunner(uc, level=BASIC, collector=collector)` |
| Emitir metricas | `BasicCollector(metrics, level=...)` |
| Tirar snapshot | `collector.snapshot()` |
| Definir metadata | `@pulse_meta(subtrack=..., feature=..., value_track=..., tags={...})` |
| Mapear via YAML | `registry.load_from_yaml(path)` + passar para runner |
| Medir trecho interno | `with pulse_span("nome", **attrs): ...` |
| Limitar spans | `BudgetPolicy(max_spans_per_execution=N)` |
| Amostrar execucoes | `SamplingPolicy(default_rate=0.5, by_value_track={...})` |
| Exportar JSON Lines | `ExportPipeline(AsyncBuffer(), JsonLinesExporter(stream))` |
| Dashboard agregado | `DashboardSummary.from_snapshot(snapshot)` |
| Validar extensoes | `ecm.register_extension(...)` + `ecm.validate_or_raise(version)` |
| Limpar dados sensiveis | `redact_keys(data)` |
| Testar sem infra | `FakeMetricsCollector()` + `BasicCollector` |
| Override no run() | `runner.run(input, value_track=..., tags={...}, extra={...})` |
| Ver contexto atual | `from forge_base.pulse import get_context; ctx = get_context()` |

### Metricas emitidas pelo BasicCollector

| Metrica | Tipo | Quando |
|---------|------|--------|
| `pulse.execution.count` | counter | on_start |
| `pulse.execution.duration_ms` | histogram | on_finish |
| `pulse.execution.errors` | counter | on_error |
| `pulse.execution.success` | counter | on_success |
