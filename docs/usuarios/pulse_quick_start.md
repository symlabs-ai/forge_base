# ForgePulse — Quick Start

Observabilidade nativa para UseCases em 5 minutos.

---

## O que e ForgePulse

ForgePulse instrumenta automaticamente a execucao de UseCases, capturando
metricas (contagem, duracao, erros), spans internos e snapshots — sem
alterar a logica de negocio. Basta envolver o UseCase com `UseCaseRunner`
e escolher um `MonitoringLevel`.

**Conceitos-chave:**

| Conceito | Descricao |
|----------|-----------|
| `MonitoringLevel` | Controla a granularidade: OFF, BASIC, STANDARD, DETAILED, DIAGNOSTIC |
| `UseCaseRunner` | Wrapper que executa o UseCase e coleta observabilidade |
| `BasicCollector` | Coletor que emite metricas e gera snapshots |
| `PulseSnapshot` | Foto do estado acumulado (execucoes, contadores, histogramas) |
| `pulse_span` | Context manager para medir trechos internos do `execute()` |

---

## Setup minimo

Instale forge_base (ForgePulse faz parte do pacote):

```bash
pip install forge_base
```

Imports necessarios para o exemplo:

```python
from forge_base.application import UseCaseBase
from forge_base.testing.fakes import FakeMetricsCollector
from forge_base.pulse import (
    BasicCollector,
    MonitoringLevel,
    UseCaseRunner,
)
```

---

## Exemplo completo

### 1. Defina um UseCase

```python
class EchoInput:
    def __init__(self, message: str) -> None:
        self.message = message

class EchoOutput:
    def __init__(self, reply: str) -> None:
        self.reply = reply

class EchoUseCase(UseCaseBase[EchoInput, EchoOutput]):
    # UseCaseBase exige 3 hooks de lifecycle.
    # Para exemplos simples basta implementar como pass.
    def _before_execute(self) -> None:
        pass

    def _after_execute(self) -> None:
        pass

    def _on_error(self, error: Exception) -> None:
        pass

    def execute(self, input_dto: EchoInput) -> EchoOutput:
        return EchoOutput(reply=f"echo: {input_dto.message}")
```

### 2. Execute com monitoramento

> **Importante:** o `level` do `BasicCollector` e do `UseCaseRunner` devem
> ser iguais. O collector usa o level para decidir quais labels/campos
> emitir; o runner usa para decidir se instrumenta a execucao.

```python
metrics = FakeMetricsCollector()
collector = BasicCollector(metrics=metrics, level=MonitoringLevel.BASIC)

runner = UseCaseRunner(
    use_case=EchoUseCase(),
    level=MonitoringLevel.BASIC,
    collector=collector,
)

result = runner.run(EchoInput("hello"))
print(result.reply)  # echo: hello
```

### 3. Tire um snapshot

```python
snapshot = collector.snapshot()

print(f"Execucoes: {len(snapshot.executions)}")
print(f"Contadores: {snapshot.counters}")
print(f"Histogramas: {list(snapshot.histograms.keys())}")
```

Saida esperada:

```
Execucoes: 1
Contadores: {'pulse.execution.count{use_case=EchoUseCase,value_track=legacy}': 1, ...}
Histogramas: ['pulse.execution.duration_ms{use_case=EchoUseCase,value_track=legacy}']
```

---

## Monitorando erros

Quando `execute()` lanca uma excecao, o runner chama `collector.on_error`
antes de re-lancar. O snapshot registra `error_type`:

```python
class FailUseCase(UseCaseBase[EchoInput, EchoOutput]):
    def _before_execute(self) -> None: pass
    def _after_execute(self) -> None: pass
    def _on_error(self, error: Exception) -> None: pass

    def execute(self, input_dto: EchoInput) -> EchoOutput:
        raise ValueError("bad input")

metrics = FakeMetricsCollector()
collector = BasicCollector(metrics=metrics, level=MonitoringLevel.BASIC)
runner = UseCaseRunner(
    use_case=FailUseCase(),
    level=MonitoringLevel.BASIC,
    collector=collector,
)

try:
    runner.run(EchoInput("boom"))
except ValueError:
    pass

snapshot = collector.snapshot()
exec_record = snapshot.executions[0]
print(exec_record["success"])     # False
print(exec_record["error_type"])  # ValueError
```

---

## Adicionando spans

`pulse_span` mede trechos internos do `execute()`. Funciona como
context manager e so tem custo quando executado dentro de um `UseCaseRunner`
com level != OFF.

```python
from forge_base.pulse import pulse_span

class EnrichUseCase(UseCaseBase[EchoInput, EchoOutput]):
    def _before_execute(self) -> None: pass
    def _after_execute(self) -> None: pass
    def _on_error(self, error: Exception) -> None: pass

    def execute(self, input_dto: EchoInput) -> EchoOutput:
        with pulse_span("validate"):
            if not input_dto.message:
                raise ValueError("empty")

        with pulse_span("transform"):
            reply = input_dto.message.upper()

        return EchoOutput(reply=reply)

metrics = FakeMetricsCollector()
collector = BasicCollector(metrics=metrics, level=MonitoringLevel.BASIC)
runner = UseCaseRunner(
    use_case=EnrichUseCase(),
    level=MonitoringLevel.BASIC,
    collector=collector,
)

runner.run(EchoInput("hi"))
snapshot = collector.snapshot()

for span in snapshot.executions[0]["spans"]:
    print(f"{span['name']}: {span['duration_ms']:.2f}ms")
```

Fora do runner, `pulse_span` e no-op (yield `None`, zero overhead).

---

## Proximos passos

Para ir alem do basico:

- **Monitoring Levels** — controle fino de granularidade (STANDARD, DETAILED, DIAGNOSTIC)
- **ValueTrackRegistry** — mapeamento de UseCases via YAML
- **@pulse_meta** — metadados estaticos por UseCase
- **SamplingPolicy** — amostragem probabilistica
- **ExportPipeline** — exportacao assincrona (JSON Lines, custom)
- **DashboardSummary** — metricas agregadas com p95

Tudo isso no [Cookbook](pulse_cookbook.md).
