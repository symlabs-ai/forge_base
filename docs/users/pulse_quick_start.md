# ForgePulse -- Quick Start

Native observability for UseCases in 5 minutes.

---

## What Is ForgePulse

ForgePulse automatically instruments UseCase execution, capturing
metrics (count, duration, errors), internal spans, and snapshots -- without
changing the business logic. Simply wrap the UseCase with `UseCaseRunner`
and choose a `MonitoringLevel`.

**Key concepts:**

| Concept | Description |
|---------|-------------|
| `MonitoringLevel` | Controls granularity: OFF, BASIC, STANDARD, DETAILED, DIAGNOSTIC |
| `UseCaseRunner` | Wrapper that executes the UseCase and collects observability |
| `BasicCollector` | Collector that emits metrics and generates snapshots |
| `PulseSnapshot` | Photo of accumulated state (executions, counters, histograms) |
| `pulse_span` | Context manager to measure internal sections of `execute()` |

---

## Minimum Setup

Install forge_base (ForgePulse is part of the package):

```bash
pip install forge_base
```

Required imports for the example:

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

## Complete Example

### 1. Define a UseCase

```python
class EchoInput:
    def __init__(self, message: str) -> None:
        self.message = message

class EchoOutput:
    def __init__(self, reply: str) -> None:
        self.reply = reply

class EchoUseCase(UseCaseBase[EchoInput, EchoOutput]):
    # UseCaseBase requires 3 lifecycle hooks.
    # For simple examples, just implement them as pass.
    def _before_execute(self) -> None:
        pass

    def _after_execute(self) -> None:
        pass

    def _on_error(self, error: Exception) -> None:
        pass

    def execute(self, input_dto: EchoInput) -> EchoOutput:
        return EchoOutput(reply=f"echo: {input_dto.message}")
```

### 2. Execute with monitoring

> **Important:** the `level` of `BasicCollector` and `UseCaseRunner` must
> be the same. The collector uses the level to decide which labels/fields
> to emit; the runner uses it to decide whether to instrument the execution.

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

### 3. Take a snapshot

```python
snapshot = collector.snapshot()

print(f"Executions: {len(snapshot.executions)}")
print(f"Counters: {snapshot.counters}")
print(f"Histograms: {list(snapshot.histograms.keys())}")
```

Expected output:

```
Executions: 1
Counters: {'pulse.execution.count{use_case=EchoUseCase,value_track=legacy}': 1, ...}
Histograms: ['pulse.execution.duration_ms{use_case=EchoUseCase,value_track=legacy}']
```

---

## Monitoring Errors

When `execute()` throws an exception, the runner calls `collector.on_error`
before re-raising. The snapshot records `error_type`:

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

## Adding Spans

`pulse_span` measures internal sections of `execute()`. It works as a
context manager and only has cost when executed inside a `UseCaseRunner`
with level != OFF.

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

Outside the runner, `pulse_span` is a no-op (yields `None`, zero overhead).

---

## Next Steps

To go beyond the basics:

- **Monitoring Levels** -- fine-grained granularity control (STANDARD, DETAILED, DIAGNOSTIC)
- **ValueTrackRegistry** -- UseCase mapping via YAML
- **@pulse_meta** -- static metadata per UseCase
- **SamplingPolicy** -- probabilistic sampling
- **ExportPipeline** -- asynchronous export (JSON Lines, custom)
- **DashboardSummary** -- aggregated metrics with p95

All of this in the [Cookbook](pulse_cookbook.md).
