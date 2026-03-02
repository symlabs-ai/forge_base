# ForgePulse — Plano de Projeto

Documento central de implementacao do ForgePulse: camada opcional de instrumentacao
por ValueTrack com governanca CL/CE.

**Origem:** [ForgePulse_PROPOSAL.md](ForgePulse_PROPOSAL.md)
**ADRs relacionados:** [003-observability-first](adr/003-observability-first.md), [007-opentelemetry-integration](adr/007-opentelemetry-integration.md)
**Versao base:** ForgeBase 0.2.0
**Status:** Em planejamento

---

## Indice

1. [Visao e Principios](#1-visao-e-principios)
2. [Arquitetura CL/CE](#2-arquitetura-clce)
3. [Decisoes Tecnicas Chave](#3-decisoes-tecnicas-chave)
4. [Mapa de Fases](#4-mapa-de-fases)
5. [Fase 0 — Fundacao (no-op)](#5-fase-0--fundacao-no-op)
6. [Fase 1 — BASIC/STANDARD + Heuristica Legado](#6-fase-1--basicstandard--heuristica-legado)
7. [Fase 2 — Mapeamento por Spec (CE)](#7-fase-2--mapeamento-por-spec-ce)
8. [Fase 3 — Decorators Opcionais + Tracing](#8-fase-3--decorators-opcionais--tracing)
9. [Fase 4 — Governanca Avancada](#9-fase-4--governanca-avancada)
10. [Fase 5 — Strict Mode + Relatorios](#10-fase-5--strict-mode--relatorios)
11. [Codigo Existente Reaproveitado](#11-codigo-existente-reaproveitado)
12. [Estrategia de Testes](#12-estrategia-de-testes)
13. [Riscos e Mitigacoes](#13-riscos-e-mitigacoes)
14. [Glossario](#14-glossario)

---

## 1. Visao e Principios

### Problema

O ForgeBase mede "saude tecnica" (logs, metricas, traces), mas nao mede "valor entregue por eixo".
Sem essa conexao, roadmap vira narrativa e cada produto instrumenta do seu jeito.

### Objetivo

Adicionar ao ForgeBase uma camada opcional (`pulse/`) que instrumenta execucoes por ValueTrack
sem quebrar compatibilidade, preservando Clean Architecture e permitindo governanca CL/CE.

### Principios Inviolaveis

| # | Principio | Verificacao |
|---|-----------|-------------|
| P1 | **Compatibilidade total** — ForgeBase sem ForgePulse continua identico | Todos os 248+ testes passam sem mudanca |
| P2 | **Opt-in** — Nada obrigatorio. Decorators sao metadata opcional | UseCase nao importa nada de `pulse/` |
| P3 | **Clean Architecture intacta** — UseCases nao dependem de infra | import-linter valida boundaries |
| P4 | **Overhead controlado** — OFF = custo zero real | Benchmark: < 100ns overhead em OFF |
| P5 | **Schema estavel** — Eventos/metricas seguem versao | Dataclass versionado com campo `schema_version` |

---

## 2. Arquitetura CL/CE

### CL — Core Logic (nucleo estavel, vive em `forge_base`)

Permanece confiavel, consistente e compativel:

- Runtime de execucao (engine)
- Contratos (interfaces/tipos) e schema base
- Propagacao de contexto (`ExecutionContext`)
- Mecanismos de plugin/hook e governanca
- Protocolos de observabilidade (`LoggerProtocol`, `MetricsProtocol`)

**CL nao contem:** regras de cliente, politica especifica, exporter especifico.

### CE — Customer Extensions (extensoes configuraveis, vivem no produto)

Varia por projeto/tenant/produto/ambiente:

- Mapeamentos de ValueTracks/SubTracks para UseCases (via spec YAML)
- Politicas de monitoramento (nivel, sampling, budgets)
- Exporters/sinks (OTEL/Prometheus/ClickHouse/arquivo)
- Relatorios customizados
- Classificacoes de risco e tags

**CE nao pode furar o CL. CE pluga via contrato (protocols).**

### Onde a instrumentacao acontece

```
Adapter (HTTP/CLI)
    |
    v
UseCaseRunner (composition root)  <-- cria ExecutionContext, mede inicio/fim/erro
    |
    v
UseCaseBase.execute()             <-- permanece PURO, sem dependencia de pulse
    |
    v
Port/Repository                   <-- adapters medem custo/latencia/retry via protocols
```

---

## 3. Decisoes Tecnicas Chave

### DT-1: Propagacao de contexto via `contextvars`

**Problema:** Injetar `ExecutionContext` no `execute(input_dto)` viola Clean Architecture.
Thread-local (`threading.local`) nao funciona com async.

**Decisao:** Usar `contextvars.ContextVar` (stdlib, async-safe).

```python
# pulse/context.py
from contextvars import ContextVar
_current_context: ContextVar[ExecutionContext | None] = ContextVar('pulse_ctx', default=None)
```

O `UseCaseRunner` seta o contexto antes de chamar `execute()`.
Qualquer camada le sem dependencia explicita. A assinatura de `execute()` nao muda.

**Referencia:** `LogContext` em `log_service.py:67-107` ja usa pattern similar com `threading.local`.

### DT-2: Protocolo de metricas separado (sem quebrar MetricsProtocol)

**Problema:** O `MetricsProtocol` atual (`composition/protocols.py:51-73`) so tem `increment()` e `timing()`.
ForgePulse precisa de `histogram()` e `gauge()`. Estender o protocolo existente quebra mypy/pyright
para qualquer classe que implemente `MetricsProtocol` sem os novos metodos.

**Decisao:** Manter `MetricsProtocol` intacto. ForgePulse define `PulseMetricsProtocol` proprio.

```python
# pulse/protocols.py
class PulseMetricsProtocol(Protocol):
    """Protocolo estendido para pulse. Nao altera MetricsProtocol existente."""
    def increment(self, name: str, value: int = 1, **tags: Any) -> None: ...
    def timing(self, name: str, value: float, **tags: Any) -> None: ...
    def histogram(self, name: str, value: float, **tags: Any) -> None: ...
    def gauge(self, name: str, value: float, **tags: Any) -> None: ...
```

`TrackMetrics` ja implementa todos os 4 metodos — satisfaz `PulseMetricsProtocol` sem mudanca.
`MetricsProtocol` original permanece com `increment()` e `timing()` — zero breaking change.

**Resultado:** typing no ecossistema nao falha ao atualizar para 0.3.0.

### DT-3: Niveis de monitoramento como enum com fast-path

**Decisao:** Enum `MonitoringLevel` com check de nivel antes de qualquer alocacao.

```python
class MonitoringLevel(IntEnum):
    OFF = 0
    BASIC = 1
    STANDARD = 2
    DETAILED = 3
    DIAGNOSTIC = 4
```

Usando `IntEnum`, o check `if level >= MonitoringLevel.STANDARD` e uma comparacao de inteiros (~1ns).
Em OFF, o `UseCaseRunner` faz passthrough direto — nenhum `ExecutionContext` criado,
nenhum `ContextVar` setado, nenhum dict alocado. Ver DT-3b.

### DT-3b: Fast-path real em OFF (sem alocacao)

**Problema:** Criar `ExecutionContext` (frozen dataclass) + `ContextVar.set()` custa ~200-500ns.
A meta "OFF < 100ns" e inatingivel se qualquer objeto for criado.

**Decisao:** Em OFF, o `UseCaseRunner.run()` e passthrough direto:

```python
def run(self, input_dto: TInput, **ctx_overrides: Any) -> TOutput:
    if self._level == MonitoringLevel.OFF:
        return self._use_case.execute(input_dto)  # zero overhead
    # ... contexto, medicao, coleta (somente level > OFF)
```

- OFF: nao cria ExecutionContext, nao seta ContextVar, nao mede tempo
- BASIC+: cria contexto completo, seta ContextVar, mede tempo

**Criterio:** benchmark com runner real (nao microbenchmark isolado).

Benchmarks sao executados em maquina de referencia e validados por comparacao
relativa (`runner.run()` vs `use_case.execute()` direto), para evitar flutuacoes
de nanosegundos por ambiente.

### DT-4: ECM adiado para Fase 4

**Decisao:** Extension Compatibility Matrix so faz sentido quando existirem extensoes CE reais
publicadas como pacotes separados. Ate la, confiar no versionamento semantico normal.

### DT-5: Relatorios sao dados estruturados, nao documentos

**Decisao:** ForgePulse CL expoe dataclasses com dados brutos (`PulseReport`).
Formatacao em Markdown/JSON e responsabilidade de CE ou do produto consumidor.

### DT-6: Schema padrao de field names (contrato CL, implementacao CE)

**Problema:** Sem contrato de nomenclatura, cada CE inventa nomes para as mesmas metricas
("llm_tokens", "tokensIn", "prompt_tokens") e a comparabilidade entre produtos morre.

**Decisao:** O CL define `PulseFieldNames` — constantes com nomes padronizados para campos
comuns (LLM, HTTP, DB, etc.). O CL **nao mede nada** — so define o envelope/shape aceito.
CE implementa wrappers/exporters que populam esses campos (ou nao).

```python
# pulse/field_names.py
class PulseFieldNames:
    """Nomes padrao para campos de metricas/eventos. CL define shape, CE popula."""

    # LLM (opcional — CE de LLM usa; outros ignoram)
    LLM_TOKENS_IN = "llm.tokens_in"
    LLM_TOKENS_OUT = "llm.tokens_out"
    LLM_LATENCY_MS = "llm.latency_ms"
    LLM_MODEL = "llm.model"
    LLM_COST = "llm.cost"
    LLM_FALLBACK_TRIGGERED = "llm.fallback_triggered"

    # HTTP (opcional)
    HTTP_METHOD = "http.method"
    HTTP_STATUS_CODE = "http.status_code"
    HTTP_LATENCY_MS = "http.latency_ms"

    # DB (opcional)
    DB_OPERATION = "db.operation"
    DB_LATENCY_MS = "db.latency_ms"
    DB_ROWS_AFFECTED = "db.rows_affected"
```

Isso e CL/CE classico: contrato no CL, implementacao no CE. Sem dependencia de
cliente OpenAI/Claude/etc. no core.

**Entrega:** documentado e publicado na 0.3.0 como contrato v0.1. Implementacao de
collectors especificos fica em CE.

**Disciplina de tags:** `correlation_id` nunca e label de metrica; dados de usuario
nao entram como tag. Identificadores de alta cardinalidade sao restritos a tracing
(DETAILED).

### DT-7: Redaction baseline desde o dia 1

**Problema:** `ExecutionContext.extra: dict[str, Any]` e `ctx_overrides` aceitam dados
arbitrarios. Sem politica minima, chaves sensiveis (`password`, `token`, `secret`,
`authorization`, `api_key`) podem vazar para exporters/logs desde a primeira coleta.

**Decisao:** Fase 0 inclui `RedactionPolicy` minima aplicada na criacao do
`ExecutionContext` (quando `level > OFF`):

```python
# pulse/redaction.py
SENSITIVE_PATTERNS: frozenset[str] = frozenset({
    "password", "passwd", "token", "secret",
    "authorization", "api_key", "apikey",
    "credential", "private_key",
})

def redact_keys(data: dict[str, Any], mask: str = "***") -> dict[str, Any]:
    """Mascara valores de chaves sensiveis. Aplicado antes de qualquer export."""
    return {
        k: mask if _is_sensitive(k) else v
        for k, v in data.items()
    }
```

- Denylist minima em frozenset (custo de lookup O(1))
- Aplicada no ponto de coleta, antes do exporter receber dados
- DIAGNOSTIC **nao inclui payload bruto** por padrao — exige allowlist explicita
- CE pode estender com allowlist/denylist adicionais via policy

**Resultado:** porta fechada desde o dia 1. Custo: ~20 linhas de codigo.

Exporters recebem dados ja redigidos por padrao. Redaction e aplicada no contexto
(na criacao do `ExecutionContext`) e novamente no caminho de export.

### DT-8: Campo `mapping_source` no ExecutionContext

**Problema:** Heuristica e util, mas gera ilusao de precisao. Sem saber a origem do
mapeamento, relatorios nao conseguem distinguir "valor declarado" de "valor inferido".

**Decisao:** `ExecutionContext` inclui campo `mapping_source` desde a Fase 0:

```python
mapping_source: Literal["spec", "decorator", "heuristic", "legacy"] = "legacy"
```

- Fase 0: sempre `"legacy"` (tudo e no-op)
- Fase 1: `"heuristic"` (inferencia por classe/modulo)
- Fase 2: `"spec"` (mapeamento YAML)
- Fase 3: `"decorator"` (metadata explicita)

Relatorios podem filtrar/agregar por fonte a partir da Fase 1.

---

## 4. Mapa de Fases

ForgePulse e uma feature da serie 0.3.x. Cada fase e um patch incremental
dentro da mesma minor version, garantindo compatibilidade entre patches.

```
Fase 0 ──> Fase 1 ──> Fase 2 ──> Fase 3 ──> Fase 4 ──> Fase 5
 v0.3.0     v0.3.1     v0.3.2     v0.3.3     v0.3.4     v0.3.5

 Fundacao   BASIC/     Spec CE    Decorators  Governanca  Strict +
 (no-op)    STANDARD              + Tracing   Avancada    Relatorios
```

| Fase | Versao | Entrega Principal | Pre-requisito |
|------|--------|-------------------|---------------|
| 0 | 0.3.0 | ExecutionContext + MonitoringLevel + NoOpCollector | ForgeBase 0.2.0 |
| 1 | 0.3.1 | Coleta BASIC/STANDARD + heuristica legado | Fase 0 |
| 2 | 0.3.2 | Mapeamento ValueTrack via YAML spec | Fase 1 |
| 3 | 0.3.3 | Decorators opt-in + tracing por span | Fase 2 |
| 4 | 0.3.4 | Sampling, budgets, ECM | Fase 3 |
| 5 | 0.3.5 | Strict mode + PulseReport estruturado | Fase 4 |

**Regra de versionamento:** patches 0.3.x sao aditivos — cada patch adiciona
funcionalidade sem quebrar o que o anterior entregou. Um produto que depende de
`forge_base>=0.3.0,<0.4.0` recebe todas as fases sem breaking change.

---

## 5. Fase 0 — Fundacao (no-op)

**Patch:** 0.3.0
**Objetivo:** Infraestrutura base com custo zero quando desligada.

### Estrutura de arquivos

```
src/forge_base/pulse/
    __init__.py              # re-exports publicos
    context.py               # ExecutionContext + ContextVar
    level.py                 # MonitoringLevel enum
    collector.py             # PulseCollector (interface) + NoOpCollector
    runner.py                # UseCaseRunner (wrapa execute com contexto)
    protocols.py             # PulseMetricsProtocol + PulseExporterProtocol (contratos)
    field_names.py           # PulseFieldNames — contrato de nomenclatura (CL)
    redaction.py             # RedactionPolicy — denylist minima de chaves sensiveis
    _version.py              # PULSE_SCHEMA_VERSION = "0.1"
```

### Entregaveis

#### 5.1 — ExecutionContext (`context.py`)

```python
@dataclass(frozen=True)
class ExecutionContext:
    correlation_id: str
    tenant_id: str = "default"
    value_track: str = "legacy"
    subtrack: str = "legacy"
    feature: str = ""
    use_case: str = ""
    mapping_source: Literal["spec", "decorator", "heuristic", "legacy"] = "legacy"
    version: str = ""
    environment: str = "development"
    level: MonitoringLevel = MonitoringLevel.OFF
    extra: dict[str, Any] = field(default_factory=dict)

# Propagacao async-safe
_current_context: ContextVar[ExecutionContext | None] = ContextVar('pulse_ctx', default=None)

def get_context() -> ExecutionContext | None: ...
def set_context(ctx: ExecutionContext) -> Token: ...
```

- `frozen=True` para imutabilidade (seguro em async/threads)
- `ContextVar` da stdlib (funciona com asyncio, threads, e taskgroups)
- `extra: dict[str, Any]` — aceita valores numericos sem stringificar
- `mapping_source` — rastreia origem do mapeamento (spec/decorator/heuristic/legacy)
- Campos com defaults = legado funciona sem configurar nada
- `extra` passa por `redact_keys()` na criacao (quando level > OFF)
- `extra` aceita apenas tipos JSON-like (`str`, `int`, `float`, `bool`, `None`, `list`, `dict`);
  valores nao serializaveis sao descartados/normalizados com contador de eventos descartados

#### 5.2 — MonitoringLevel (`level.py`)

```python
class MonitoringLevel(IntEnum):
    OFF = 0           # no-op real, custo ~0
    BASIC = 1         # duration + count + success/error
    STANDARD = 2      # + latencia por adapter + erros por etapa
    DETAILED = 3      # + tracing + custo (tokens/cpu)
    DIAGNOSTIC = 4    # + profiling/payload (somente por flag)
```

#### 5.3 — PulseCollector + NoOpCollector (`collector.py`)

```python
class PulseCollector(Protocol):
    def on_start(self, ctx: ExecutionContext) -> None: ...
    def on_success(self, ctx: ExecutionContext, duration_ms: float) -> None: ...
    def on_error(self, ctx: ExecutionContext, error: Exception, duration_ms: float) -> None: ...

class NoOpCollector:
    """Custo zero. Usado quando level=OFF."""
    def on_start(self, ctx: ExecutionContext) -> None: pass
    def on_success(self, ctx: ExecutionContext, duration_ms: float) -> None: pass
    def on_error(self, ctx: ExecutionContext, error: Exception, duration_ms: float) -> None: pass
```

#### 5.4 — UseCaseRunner (`runner.py`)

```python
class UseCaseRunner(Generic[TInput, TOutput]):
    """Wrapa execute() com contexto + coleta. Vive no composition root."""

    def __init__(
        self,
        use_case: UseCaseBase[TInput, TOutput],
        collector: PulseCollector | None = None,
        level: MonitoringLevel = MonitoringLevel.OFF,
    ): ...

    def run(self, input_dto: TInput, **ctx_overrides: Any) -> TOutput:
        # FAST-PATH: OFF = passthrough direto, zero alocacao
        if self._level == MonitoringLevel.OFF:
            return self._use_case.execute(input_dto)

        # INSTRUMENTED PATH (level > OFF):
        # 1. Cria ExecutionContext (com inferencia de use_case pelo nome da classe)
        # 2. Aplica redact_keys() no extra/ctx_overrides
        # 3. Seta ContextVar
        # 4. Chama collector.on_start()
        # 5. Chama use_case.execute(input_dto)
        # 6. Chama collector.on_success() ou on_error()
        # 7. Restaura ContextVar
        # 8. Retorna resultado
        ...
```

#### 5.5 — Protocolos (`protocols.py`)

```python
class PulseMetricsProtocol(Protocol):
    """Protocolo estendido para pulse. MetricsProtocol original nao muda."""
    def increment(self, name: str, value: int = 1, **tags: Any) -> None: ...
    def timing(self, name: str, value: float, **tags: Any) -> None: ...
    def histogram(self, name: str, value: float, **tags: Any) -> None: ...
    def gauge(self, name: str, value: float, **tags: Any) -> None: ...

class PulseExporterProtocol(Protocol):
    """Contrato CE: quem quiser exportar dados implementa isto."""
    def export_execution(self, ctx: ExecutionContext, duration_ms: float, success: bool) -> None: ...
```

`TrackMetrics` ja satisfaz `PulseMetricsProtocol` sem nenhuma alteracao.
`MetricsProtocol` em `composition/protocols.py` permanece intacto.

#### 5.6 — PulseFieldNames (`field_names.py`)

Constantes de nomenclatura padrao para campos de metricas/eventos.
Contrato v0.1 — CL define shape, CE popula. Ver DT-6.

#### 5.7 — RedactionPolicy (`redaction.py`)

Denylist minima de chaves sensiveis aplicada na criacao do contexto.
Chaves como `password`, `token`, `secret`, `authorization`, `api_key` sao mascaradas.
Ver DT-7.

### Criterios de aceitacao — Fase 0

**Compatibilidade e boundaries:**
- [ ] Todos os 248+ testes existentes passam sem mudanca
- [ ] `UseCaseBase.execute()` inalterado (assinatura e comportamento)
- [ ] `MetricsProtocol` em `composition/protocols.py` inalterado (zero breaking change em typing)
- [ ] import-linter atualizado para `forge_base` (corrigir root_package) e com regras para `pulse/`:
  - `application/*` nao importa `pulse/*`
  - `domain/*` nao importa `pulse/*`
  - `pulse/*` nao importa `adapters/*` nem `infrastructure/*`
- [ ] `pulse/` nao e importado por nenhum modulo existente (zero acoplamento)
- [ ] Pipeline falha se boundary for violado

**Funcionalidade:**
- [ ] `import forge_base.pulse` funciona
- [ ] `ExecutionContext` com `extra: dict[str, Any]` (aceita valores numericos)
- [ ] `ExecutionContext.mapping_source` presente com default `"legacy"`
- [ ] `ExecutionContext` propagado via `contextvars` e legivel em qualquer camada
- [ ] `PulseMetricsProtocol` definido em `pulse/protocols.py` (nao altera MetricsProtocol existente)
- [ ] `PulseFieldNames` publicado como contrato v0.1 (nomes LLM/HTTP/DB)
- [ ] `redact_keys()` mascara chaves sensiveis (`password`, `token`, `secret`, `authorization`, `api_key`)

**Performance:**
- [ ] `UseCaseRunner` com `level=OFF` faz passthrough direto (nao cria ExecutionContext)
- [ ] Benchmark real com runner: OFF < 100ns overhead

**Documentacao:**
- [ ] ADR-008 escrito documentando decisao CL/CE e ForgePulse

### Testes novos

```
tests/unit/pulse/
    test_context.py          # ExecutionContext criacao, frozen, defaults, ContextVar, mapping_source
    test_level.py            # MonitoringLevel comparacoes, IntEnum behavior
    test_collector.py        # NoOpCollector nao faz nada, protocol check
    test_runner.py           # UseCaseRunner OFF=passthrough, com mock collector, contexto propagado
    test_protocols.py        # PulseMetricsProtocol satisfeito por TrackMetrics
    test_field_names.py      # PulseFieldNames constantes existem e sao strings
    test_redaction.py        # Chaves sensiveis mascaradas, chaves normais preservadas
tests/benchmarks/
    bench_pulse_overhead.py  # OFF < 100ns (com runner real), BASIC < 10us
```

---

## 6. Fase 1 — BASIC/STANDARD + Heuristica Legado

**Patch:** 0.3.1
**Pre-requisito:** Fase 0 completa
**Objetivo:** Primeira coleta real de metricas por use case, com fallback legado automatico.

### Estrutura de arquivos (novos)

```
src/forge_base/pulse/
    basic_collector.py       # Implementacao BASIC/STANDARD
    heuristic.py             # Inferencia automatica de value_track/feature
    report.py                # PulseSnapshot dataclass (dados brutos)
```

### Entregaveis

#### 6.1 — BasicCollector (`basic_collector.py`)

Implementa `PulseCollector` usando `TrackMetrics` existente.

**Nivel BASIC coleta:**
- `pulse.execution.count` (counter, por use_case + value_track)
- `pulse.execution.duration_ms` (histogram, por use_case + value_track)
- `pulse.execution.errors` (counter, por use_case + value_track + error_type)
- `pulse.execution.success` (counter, por use_case + value_track)

**Nivel STANDARD adiciona:**
- Metricas com label de `subtrack`
- `pulse.adapter.duration_ms` (histogram, por adapter + value_track)
- Contagem de erros por etapa (antes/durante/apos execute)

#### 6.2 — Heuristica legado (`heuristic.py`)

```python
def infer_context(use_case: UseCaseBase) -> dict[str, str]:
    """Infere value_track, subtrack, feature a partir de classe/modulo."""
    cls = type(use_case)
    module = cls.__module__           # ex: "meu_app.billing.usecases.create_invoice"
    class_name = cls.__name__         # ex: "CreateInvoiceUseCase"

    return {
        "use_case": class_name,
        "feature": _extract_feature(module),     # "create_invoice"
        "value_track": "legacy",                  # fallback
        "subtrack": _extract_domain(module),      # "billing"
    }
```

- Usa nome do modulo para inferir dominio/feature
- `value_track` fica `"legacy"` ate que spec CE forneca mapeamento (Fase 2)
- Zero configuracao necessaria

#### 6.3 — PulseSnapshot (`report.py`)

```python
@dataclass
class PulseSnapshot:
    """Dados brutos de uma janela de observacao. Nao e relatorio formatado."""
    timestamp: float
    schema_version: str
    level: MonitoringLevel
    executions: list[ExecutionRecord]
    counters: dict[str, int]
    histograms: dict[str, HistogramStats]
```

### Criterios de aceitacao — Fase 1

- [ ] `UseCaseRunner(level=BASIC)` coleta duration + count + success/error
- [ ] Heuristica infere `use_case`, `feature`, `subtrack` sem configuracao
- [ ] `value_track="legacy"` para todos os use cases sem mapeamento
- [ ] `PulseSnapshot` gerado com dados reais apos execucoes
- [ ] Overhead BASIC < 10us por execucao (benchmark)
- [ ] Integracao com `TrackMetrics` existente (reutiliza, nao duplica)
- [ ] Nenhuma mudanca em codigo existente fora de `pulse/`

### Testes novos

```
tests/unit/pulse/
    test_basic_collector.py  # Coleta correta por nivel
    test_heuristic.py        # Inferencia de contexto a partir de classe/modulo
    test_report.py           # PulseSnapshot geracao e serializacao
tests/integration/pulse/
    test_runner_basic.py     # UseCaseRunner com BasicCollector end-to-end
```

---

## 7. Fase 2 — Mapeamento por Spec (CE)

**Patch:** 0.3.2
**Pre-requisito:** Fase 1 completa
**Objetivo:** Produtos mapeiam use cases para ValueTracks reais sem mexer em codigo.

### Estrutura de arquivos (novos)

```
src/forge_base/pulse/
    value_tracks.py          # ValueTrackRegistry + loader de spec
    spec_schema.py           # Schema do YAML de mapeamento
```

### Entregaveis

#### 7.1 — ValueTrackRegistry (`value_tracks.py`)

```python
class ValueTrackRegistry:
    """Resolve use_case -> (value_track, subtrack, tags)."""

    def load_from_yaml(self, path: str) -> None: ...
    def load_from_dict(self, data: dict) -> None: ...
    def resolve(self, use_case_name: str) -> ValueTrackMapping | None: ...
```

#### 7.2 — Spec YAML (exemplo CE, nao vive no ForgeBase)

```yaml
# forgepulse.value_tracks.yml (no produto, nao na lib)
schema_version: "0.1"

value_tracks:
  cost_governance:
    description: "Governanca de custo"
    usecases:
      - CreateInvoiceUseCase
      - ProcessPaymentUseCase
    subtracks:
      billing: [CreateInvoiceUseCase]
      payments: [ProcessPaymentUseCase]
    tags:
      domain: financial
      risk: medium

  reliability:
    description: "Confiabilidade do servico"
    usecases:
      - HealthCheckUseCase
      - RetryOperationUseCase
    tags:
      domain: infrastructure
      risk: high
```

#### 7.3 — Ordem de resolucao no UseCaseRunner

```
1. ValueTrackRegistry (spec CE)     -> mapeamento explicito
2. Decorator metadata (se houver)   -> Fase 3
3. Heuristica legado (Fase 1)       -> fallback automatico
```

### Criterios de aceitacao — Fase 2

- [ ] `ValueTrackRegistry.load_from_yaml()` carrega spec valido
- [ ] `ValueTrackRegistry.resolve("CreateInvoiceUseCase")` retorna mapeamento correto
- [ ] `UseCaseRunner` consulta registry antes de heuristica
- [ ] Metricas agrupadas por `value_track` real (nao mais apenas "legacy")
- [ ] Spec invalido gera `ConfigurationError` (dominio, nao crash)
- [ ] Schema versionado (`schema_version` validado)
- [ ] Documentacao: guia CE "como mapear seus ValueTracks"

### Testes novos

```
tests/unit/pulse/
    test_value_tracks.py     # Registry load, resolve, fallback
    test_spec_schema.py      # Validacao de spec YAML valido/invalido
tests/integration/pulse/
    test_runner_with_spec.py # End-to-end com spec CE carregado
```

---

## 8. Fase 3 — Decorators Opcionais + Tracing

**Patch:** 0.3.3
**Pre-requisito:** Fase 2 completa
**Objetivo:** Precisao em modulos novos via decorators metadata-only e tracing por span.

### Estrutura de arquivos (novos)

```
src/forge_base/pulse/
    decorators.py            # @pulse_track, @pulse_span (metadata only)
    tracing.py               # Integracao com TracerPort existente
```

### Entregaveis

#### 8.1 — Decorators metadata-only (`decorators.py`)

```python
def pulse_track(
    value_track: str,
    subtrack: str = "",
    tags: dict[str, str] | None = None,
) -> Callable:
    """Marca um use case com ValueTrack. NAO instrumenta — apenas anota metadata."""
    def decorator(cls):
        cls._pulse_metadata = PulseMetadata(value_track, subtrack, tags or {})
        return cls  # nao wrapa, nao altera comportamento
    return decorator

# Uso:
@pulse_track(value_track="cost_governance", subtrack="billing")
class CreateInvoiceUseCase(UseCaseBase[CreateInvoiceInput, InvoiceOutput]):
    def execute(self, input_dto): ...
```

- Decorator **nao wrapa** a classe/metodo
- So adiciona atributo `_pulse_metadata`
- UseCaseRunner le o atributo na resolucao de contexto (prioridade 2, entre spec e heuristica)
- Se o dev nao usar, nada muda

#### 8.2 — Tracing integrado (`tracing.py`)

```python
class PulseTracer:
    """Cria spans automaticos vinculados ao ExecutionContext."""

    def __init__(self, tracer: TracerPort, level: MonitoringLevel): ...

    def execution_span(self, ctx: ExecutionContext) -> Span | None:
        """Cria span para execucao de use case. Retorna None se level < DETAILED."""
        if self.level < MonitoringLevel.DETAILED:
            return None
        ...
```

- Reutiliza `TracerPort` e `Span` existentes (`observability/tracer_port.py`)
- Spans vinculados ao `ExecutionContext.correlation_id`
- Nivel DETAILED cria spans; BASIC/STANDARD nao

### Criterios de aceitacao — Fase 3

- [ ] `@pulse_track` nao altera comportamento da classe (zero overhead)
- [ ] `UseCaseRunner` resolve metadata de decorator (prioridade 2)
- [ ] Ordem final: Spec > Decorator > Heuristica
- [ ] Nivel DETAILED cria spans vinculados ao contexto
- [ ] Spans reusam `TracerPort` existente (nao cria sistema paralelo)
- [ ] `NoOpTracer` continua funcionando (DETAILED sem tracer = noop)
- [ ] Decorators sao opcionais — nenhum modulo existente precisa deles

### Testes novos

```
tests/unit/pulse/
    test_decorators.py       # Metadata setada, classe nao alterada, prioridade
    test_tracing.py          # Spans criados por nivel, vinculacao ao contexto
tests/integration/pulse/
    test_runner_decorated.py # Runner + decorator + spec + heuristica combinados
```

---

## 9. Fase 4 — Governanca Avancada

**Patch:** 0.3.4
**Pre-requisito:** Fase 3 completa
**Objetivo:** Controle fino de custo de telemetria e validacao de extensoes.

### Estrutura de arquivos (novos)

```
src/forge_base/pulse/
    policy.py                # SamplingPolicy, BudgetPolicy
    ecm.py                   # ExtensionCompatibilityMatrix
    buffer.py                # AsyncBuffer com drop controlado
```

### Entregaveis

#### 9.1 — Sampling Policy (`policy.py`)

```python
@dataclass
class SamplingPolicy:
    """Decide se uma execucao deve ser instrumentada."""
    default_rate: float = 1.0                    # 100% por padrao
    by_value_track: dict[str, float] = field(default_factory=dict)
    by_tenant: dict[str, float] = field(default_factory=dict)

    def should_sample(self, ctx: ExecutionContext) -> bool: ...
```

#### 9.2 — Budget Policy (`policy.py`)

```python
@dataclass
class BudgetPolicy:
    """Limita quantidade de telemetria por execucao."""
    max_spans_per_execution: int = 100
    max_events_per_execution: int = 50
    max_bytes_per_execution: int = 64 * 1024   # 64KB
```

#### 9.3 — ECM (`ecm.py`)

```python
class ExtensionCompatibilityMatrix:
    """Valida se extensoes CE sao compativeis com a versao do ForgeBase/Pulse."""

    def register_extension(self, name: str, version: str, requires_pulse: str): ...
    def validate(self, pulse_version: str) -> list[IncompatibleExtension]: ...
    def validate_or_raise(self, pulse_version: str) -> None: ...
```

- Validacao no startup via `BuilderBase`
- Extensao incompativel: desabilita (warn) ou falha (strict), conforme policy
- Estrutura leve — sem banco, sem rede, sem lock

#### 9.4 — AsyncBuffer (`buffer.py`)

```python
class AsyncBuffer:
    """Buffer assincrono para exportacao com drop controlado."""

    def __init__(self, max_size: int = 10_000, drop_policy: str = "oldest"): ...
    def push(self, record: ExecutionRecord) -> bool: ...   # False se dropou
    def flush(self, exporter: PulseExporterProtocol) -> int: ...  # retorna N exportados
```

### Criterios de aceitacao — Fase 4

- [ ] Sampling por value_track e tenant funciona
- [ ] Budget limita spans/eventos/bytes por execucao
- [ ] ECM valida extensoes no startup
- [ ] Extensao incompativel gera warning ou erro conforme policy
- [ ] AsyncBuffer com drop controlado nao bloqueia runtime
- [ ] Overhead de policy check < 1us

### Testes novos

```
tests/unit/pulse/
    test_policy.py           # Sampling rates, budget limits
    test_ecm.py              # Compatibilidade, incompatibilidade, strict mode
    test_buffer.py           # Capacidade, drop, flush
tests/property_based/
    test_sampling_properties.py  # Taxa de sampling converge para o esperado
```

---

## 10. Fase 5 — Strict Mode + Relatorios

**Patch:** 0.3.5
**Pre-requisito:** Fase 4 completa
**Objetivo:** Modo strict por escopo e dados estruturados para relatorios.

### Estrutura de arquivos (novos)

```
src/forge_base/pulse/
    strict.py                # StrictMode: valida que todo use case tem ValueTrack
    report.py                # (estende) PulseReport com agregacoes
```

### Entregaveis

#### 10.1 — Strict Mode (`strict.py`)

```python
class StrictMode:
    """Valida que todos os use cases em um escopo tem ValueTrack mapeado."""

    def __init__(self, scope: str = "*"):  # scope pode ser modulo ou package
        ...

    def validate(self, registry: ValueTrackRegistry, discovered: list[str]) -> StrictReport:
        """Retorna lista de use cases sem mapeamento."""
        ...
```

- Ativado por escopo (ex: `scope="meu_app.billing"`)
- Nao bloqueia execucao — gera relatorio
- `StrictReport` expoe `ok: bool` e `missing: list[str]`
- Em CI, `assert_ok()` falha o pipeline quando `ok=False`
- Util para CI: fail se use case novo sem ValueTrack

#### 10.2 — PulseReport estendido (`report.py`)

```python
@dataclass
class PulseReport:
    """Dados estruturados para consumo por relatorios CE."""
    snapshot: PulseSnapshot
    by_value_track: dict[str, ValueTrackStats]
    by_tenant: dict[str, TenantStats]
    unmapped_usecases: list[str]
    schema_version: str

@dataclass
class ValueTrackStats:
    total_executions: int
    error_rate: float
    p50_duration_ms: float
    p95_duration_ms: float
    p99_duration_ms: float
```

- **Dados brutos, nao relatorio formatado**
- CE ou produto converte para Markdown/JSON/dashboard

### Criterios de aceitacao — Fase 5

- [ ] StrictMode identifica use cases sem mapeamento
- [ ] PulseReport agrega por value_track e tenant
- [ ] Dados exportaveis como dict/JSON
- [ ] Integravel com CI (exit code != 0 se strict falha)
- [ ] Documentacao completa: guia de adocao por fase

---

## 11. Codigo Existente Reaproveitado

Inventario do que ja existe e sera reutilizado (nao reimplementado):

| Componente | Arquivo | Uso no ForgePulse |
|------------|---------|-------------------|
| `TrackMetrics` | `observability/track_metrics.py` | Backend de metricas para BasicCollector |
| `LogService` + `LogContext` | `observability/log_service.py` | Pattern de context propagation (referencia para DT-1) |
| `TracerPort` + `Span` | `observability/tracer_port.py` | Backend de tracing para Fase 3 |
| `NoOpTracer` | `observability/tracer_port.py:325` | Pattern para nivel OFF |
| `InMemoryTracer` | `observability/tracer_port.py:377` | Tracing em dev/testes |
| `@track_metrics` | `application/decorators/track_metrics.py` | Pattern para decorators opt-in (referencia para Fase 3) |
| `BuilderBase` | `composition/builder.py` | Composition root onde Runner se pluga |
| `BuildContextBase` | `composition/build_context.py` | Context com cache, env resolution |
| `BuildSpecBase` | `composition/build_spec.py` | Base para spec YAML de ValueTracks |
| `PluginRegistryBase` | `composition/plugin_registry.py` | Base para ECM |
| `LoggerProtocol` | `composition/protocols.py` | Contrato de logging |
| `MetricsProtocol` | `composition/protocols.py` | Contrato de metricas (permanece intacto; pulse usa `PulseMetricsProtocol`) |
| `UseCaseBase` | `application/usecase_base.py` | Interface que Runner wrapa (nao modifica) |
| `DependencyContainer` | `core_init.py` | DI para registrar Pulse services |

---

## 12. Estrategia de Testes

### Por tipo

| Tipo | Diretorio | O que valida |
|------|-----------|--------------|
| Unit | `tests/unit/pulse/` | Cada componente isolado |
| Integration | `tests/integration/pulse/` | Runner + Collector + Registry end-to-end |
| Property-based | `tests/property_based/` | Sampling convergencia, context imutabilidade |
| Benchmark | `tests/benchmarks/` | Overhead por nivel (OFF < 100ns, BASIC < 10us) |
| Contract | `tests/contract_tests/` | PulseCollector protocol compliance |
| Regression | Todos os 248+ existentes | Nada quebra (P1) |

### Regra de ouro

**Nenhum teste existente pode ser modificado ou removido por causa do ForgePulse.**
Se um teste existente falha, e bug no ForgePulse, nao no teste.

### Markers pytest

```ini
[tool:pytest]
markers =
    pulse: ForgePulse tests
    pulse_benchmark: Overhead benchmarks
```

---

## 13. Riscos e Mitigacoes

| # | Risco | Impacto | Mitigacao |
|---|-------|---------|-----------|
| R1 | Scope creep — cada fase atrai "mais uma feature" | Alto | Cada fase tem criterios de aceitacao fechados. Feature extra vai para fase seguinte. |
| R2 | Performance — instrumentacao degrada runtime | Alto | Benchmarks obrigatorios por fase. OFF = passthrough direto comprovado. |
| R3 | Acoplamento — pulse contamina camadas existentes | Alto | import-linter valida boundaries. Pipeline falha se violado. |
| R4 | Typing quebra no ecossistema | Medio | `MetricsProtocol` intacto. Pulse usa `PulseMetricsProtocol` proprio (DT-2). |
| R5 | Ninguem usa ValueTracks na pratica | Medio | Heuristica legado garante valor desde Fase 1 sem configuracao. |
| R6 | Complexidade de contextvars com frameworks web | Medio | Testar com Flask, FastAPI. Frameworks ASGI propagam contextvars nativamente. |
| R7 | YAML spec cresce sem governanca | Baixo | Schema versionado + validacao na Fase 2. |
| R8 | Vazamento de PII via `extra`/tags | Alto | `RedactionPolicy` com denylist desde a Fase 0 (DT-7). DIAGNOSTIC exige allowlist explicita. |

---

## 14. Glossario

| Termo | Definicao |
|-------|-----------|
| **ValueTrack** | Eixo de valor mensuravel (ex: Governanca de Custo, Confiabilidade, Seguranca) |
| **SubTrack** | Subdivisao de um ValueTrack (ex: billing, payments dentro de cost_governance) |
| **CL** | Core Logic — nucleo estavel do ForgeBase |
| **CE** | Customer Extensions — extensoes configuraveis por produto/cliente |
| **ECM** | Extension Compatibility Matrix — validacao de compatibilidade de extensoes |
| **MonitoringLevel** | Nivel de instrumentacao (OFF/BASIC/STANDARD/DETAILED/DIAGNOSTIC) |
| **ExecutionContext** | Contexto imutavel propagado por toda a execucao via contextvars |
| **PulseCollector** | Interface para coleta de metricas por nivel |
| **UseCaseRunner** | Wrapper no composition root que instrumenta execute() sem alterar UseCase |
| **PulseSnapshot** | Dados brutos de uma janela de observacao |
| **PulseReport** | Agregacao estruturada para consumo por relatorios |
| **Heuristica legado** | Inferencia automatica de contexto por nome de classe/modulo |
| **Sampling** | Amostragem probabilistica para controle de volume |
| **Budget** | Limite de telemetria por execucao (spans, eventos, bytes) |
| **Strict Mode** | Validacao de que todo use case tem ValueTrack mapeado |
| **PulseFieldNames** | Constantes de nomenclatura padrao para campos de metricas (contrato CL) |
| **PulseMetricsProtocol** | Protocolo estendido de metricas para pulse (nao altera MetricsProtocol) |
| **RedactionPolicy** | Denylist de chaves sensiveis aplicada na coleta de dados |
| **mapping_source** | Campo que identifica origem do mapeamento (spec/decorator/heuristic/legacy) |

---

## 15. Plano de Execucao e Registro de Evolucao

### Convencoes

- Cada fase e um PR unico. PR so e mergeado quando todos os criterios de aceitacao estao verdes.
- Registro de evolucao e feito neste documento (secao 15.2) ao concluir cada fase.
- Bloqueios sao registrados com data, descricao e resolucao.
- Decisoes tomadas durante a implementacao que desviem do plano sao anotadas como "Desvio".

### 15.1 — Checklist de Execucao

#### Pre-Fase 0: Preparacao do terreno

- [ ] Corrigir `.import-linter`: `root_package = forgebase` -> `root_package = forge_base`
- [ ] Validar que import-linter roda e passa com config corrigido
- [ ] Confirmar que todos os 248+ testes passam no estado atual (baseline)

#### Fase 0 — Fundacao (0.3.0)

| # | Tarefa | Arquivo(s) | Status |
|---|--------|------------|--------|
| F0.1 | Criar `pulse/` package com `__init__.py` | `pulse/__init__.py` | Pendente |
| F0.2 | Implementar `MonitoringLevel` (IntEnum) | `pulse/level.py` | Pendente |
| F0.3 | Implementar `ExecutionContext` (frozen dataclass + ContextVar) | `pulse/context.py` | Pendente |
| F0.4 | Implementar `PulseCollector` (Protocol) + `NoOpCollector` | `pulse/collector.py` | Pendente |
| F0.5 | Implementar `PulseMetricsProtocol` + `PulseExporterProtocol` | `pulse/protocols.py` | Pendente |
| F0.6 | Implementar `PulseFieldNames` (constantes v0.1) | `pulse/field_names.py` | Pendente |
| F0.7 | Implementar `redact_keys()` + denylist | `pulse/redaction.py` | Pendente |
| F0.8 | Implementar `UseCaseRunner` com fast-path OFF | `pulse/runner.py` | Pendente |
| F0.9 | Criar `_version.py` com `PULSE_SCHEMA_VERSION` | `pulse/_version.py` | Pendente |
| F0.10 | Adicionar regras import-linter para `pulse/` | `.import-linter` | Pendente |
| F0.11 | Escrever testes unitarios (context, level, collector, runner, protocols, redaction) | `tests/unit/pulse/` | Pendente |
| F0.12 | Escrever benchmark OFF vs execute direto | `tests/benchmarks/` | Pendente |
| F0.13 | Escrever ADR-008 (CL/CE + ForgePulse) | `docs/adr/008-forgepulse-clce.md` | Pendente |
| F0.14 | Rodar suite completa (248+ testes antigos + novos) | CI | Pendente |
| F0.15 | Bump version para 0.3.0, tag, CHANGELOG | `pyproject.toml`, `CHANGELOG.md` | Pendente |

#### Fase 1 — BASIC/STANDARD (0.3.1)

| # | Tarefa | Arquivo(s) | Status |
|---|--------|------------|--------|
| F1.1 | Implementar `BasicCollector` (BASIC + STANDARD) | `pulse/basic_collector.py` | Pendente |
| F1.2 | Implementar `infer_context()` heuristica | `pulse/heuristic.py` | Pendente |
| F1.3 | Implementar `PulseSnapshot` + `ExecutionRecord` | `pulse/report.py` | Pendente |
| F1.4 | Integrar `BasicCollector` com `TrackMetrics` existente | `pulse/basic_collector.py` | Pendente |
| F1.5 | Testes unitarios (basic_collector, heuristic, report) | `tests/unit/pulse/` | Pendente |
| F1.6 | Teste integracao Runner + BasicCollector end-to-end | `tests/integration/pulse/` | Pendente |
| F1.7 | Benchmark BASIC < 10us | `tests/benchmarks/` | Pendente |
| F1.8 | Bump version para 0.3.1, tag, CHANGELOG | `pyproject.toml`, `CHANGELOG.md` | Pendente |

#### Fase 2 — Mapeamento por Spec (0.3.2)

| # | Tarefa | Arquivo(s) | Status |
|---|--------|------------|--------|
| F2.1 | Implementar `ValueTrackRegistry` (load YAML, resolve) | `pulse/value_tracks.py` | Pendente |
| F2.2 | Implementar validacao de schema YAML | `pulse/spec_schema.py` | Pendente |
| F2.3 | Integrar registry no `UseCaseRunner` (spec > heuristica) | `pulse/runner.py` | Pendente |
| F2.4 | Testes unitarios (value_tracks, spec_schema) | `tests/unit/pulse/` | Pendente |
| F2.5 | Teste integracao Runner + spec CE | `tests/integration/pulse/` | Pendente |
| F2.6 | Documentacao: guia CE "como mapear seus ValueTracks" | `docs/usuarios/` | Pendente |
| F2.7 | Bump version para 0.3.2, tag, CHANGELOG | `pyproject.toml`, `CHANGELOG.md` | Pendente |

#### Fase 3 — Decorators + Tracing (0.3.3)

| # | Tarefa | Arquivo(s) | Status |
|---|--------|------------|--------|
| F3.1 | Implementar `@pulse_track` (metadata-only) | `pulse/decorators.py` | Pendente |
| F3.2 | Implementar `PulseTracer` (integracao com `TracerPort`) | `pulse/tracing.py` | Pendente |
| F3.3 | Integrar decorator no Runner (spec > decorator > heuristica) | `pulse/runner.py` | Pendente |
| F3.4 | Implementar `RedactionPolicy` completa para DIAGNOSTIC | `pulse/redaction.py` | Pendente |
| F3.5 | Testes unitarios (decorators, tracing) | `tests/unit/pulse/` | Pendente |
| F3.6 | Teste integracao Runner + decorator + spec + heuristica | `tests/integration/pulse/` | Pendente |
| F3.7 | Bump version para 0.3.3, tag, CHANGELOG | `pyproject.toml`, `CHANGELOG.md` | Pendente |

#### Fase 4 — Governanca Avancada (0.3.4)

| # | Tarefa | Arquivo(s) | Status |
|---|--------|------------|--------|
| F4.1 | Implementar `SamplingPolicy` + `BudgetPolicy` | `pulse/policy.py` | Pendente |
| F4.2 | Implementar `ExtensionCompatibilityMatrix` | `pulse/ecm.py` | Pendente |
| F4.3 | Implementar `AsyncBuffer` com drop controlado | `pulse/buffer.py` | Pendente |
| F4.4 | Testes unitarios (policy, ecm, buffer) | `tests/unit/pulse/` | Pendente |
| F4.5 | Testes property-based (sampling convergencia) | `tests/property_based/` | Pendente |
| F4.6 | Bump version para 0.3.4, tag, CHANGELOG | `pyproject.toml`, `CHANGELOG.md` | Pendente |

#### Fase 5 — Strict Mode + Relatorios (0.3.5)

| # | Tarefa | Arquivo(s) | Status |
|---|--------|------------|--------|
| F5.1 | Implementar `StrictMode` + `StrictReport` (`ok`, `missing`, `assert_ok()`) | `pulse/strict.py` | Pendente |
| F5.2 | Implementar `PulseReport` + `ValueTrackStats` com `to_dict()` | `pulse/report.py` | Pendente |
| F5.3 | Testes unitarios (strict, report serializacao) | `tests/unit/pulse/` | Pendente |
| F5.4 | Teste integracao CI (strict mode falha pipeline) | `tests/integration/pulse/` | Pendente |
| F5.5 | Documentacao completa: guia de adocao por fase | `docs/usuarios/` | Pendente |
| F5.6 | Bump version para 0.3.5, tag, CHANGELOG | `pyproject.toml`, `CHANGELOG.md` | Pendente |

---

### 15.2 — Registro de Evolucao

Historico de execucao. Atualizar ao concluir cada fase.

#### Fase 0

| Data | Evento | Notas |
|------|--------|-------|
| — | *Ainda nao iniciada* | — |

#### Fase 1

| Data | Evento | Notas |
|------|--------|-------|
| — | *Ainda nao iniciada* | — |

#### Fase 2

| Data | Evento | Notas |
|------|--------|-------|
| — | *Ainda nao iniciada* | — |

#### Fase 3

| Data | Evento | Notas |
|------|--------|-------|
| — | *Ainda nao iniciada* | — |

#### Fase 4

| Data | Evento | Notas |
|------|--------|-------|
| — | *Ainda nao iniciada* | — |

#### Fase 5

| Data | Evento | Notas |
|------|--------|-------|
| — | *Ainda nao iniciada* | — |

---

### 15.3 — Registro de Bloqueios

| Data | Fase | Descricao | Resolucao | Status |
|------|------|-----------|-----------|--------|
| — | — | *Nenhum bloqueio registrado* | — | — |

---

### 15.4 — Registro de Desvios

Decisoes tomadas durante a implementacao que divergem do plano original.

| Data | Fase | Desvio | Justificativa | Impacto |
|------|------|--------|---------------|---------|
| — | — | *Nenhum desvio registrado* | — | — |

---

*Documento vivo. Atualizar a cada fase concluida.*
