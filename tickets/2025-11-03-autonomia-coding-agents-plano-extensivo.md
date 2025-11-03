# Ticket: Plano Extensivo para Aumentar a Autonomia de Coding Agents no ForgeBase

Responsável: a designar
Status: Novo
Data: 2025-11-03
Prioridade: Alta (P1) — rollout incremental

## Introdução — Racional

Agentes de RIA operam melhor quando o ambiente oferece contratos fortes, feedback rápido e caminhos padronizados. No ForgeBase, isso se traduz em:

- Tipagem forte e contratos estáveis (erros cedo, refactors seguros);
- Observabilidade como API (métricas/logs que guiam decisões automáticas);
- Testes de contrato (adapters/ports validáveis sem intervenção humana);
- Scaffoldings e exemplos (geração de código consistente e rastreável);
- Guardrails arquiteturais (evitar violações de camadas e dependências frágeis).

O objetivo deste plano é estabelecer esses pilares de modo incremental, priorizando impacto versus esforço, sem poluir a raiz do repositório (configs em `scripts/`), e mantendo coerência Clean + Hexagonal + Observável.

---

## 1) Tipagem Forte e Contratos Estáticos (Mypy strict + Protocols/Generics)

Objetivo: Garantir que agentes tenham feedback imediato sobre contratos, reduzindo ambiguidade e runtime errors.

Pontos-chave:
- Adotar Mypy em modo estrito (mypy.ini em `scripts/`), iniciando por `domain/` e expandindo.
- Usar `Protocol`/`ABC` e generics nos Ports/Repos; DTOs tipados.

Exemplo — Port com Protocol + genéricos:
```python
from typing import Protocol, TypeVar, Generic
from forgebase.domain.entity_base import EntityBase

T = TypeVar("T", bound=EntityBase)

class RepositoryPort(Protocol, Generic[T]):
    def save(self, entity: T) -> None: ...
    def find_by_id(self, id: str) -> T | None: ...
    def find_all(self) -> list[T]: ...
    def delete(self, id: str) -> None: ...
    def exists(self, id: str) -> bool: ...
```

Exemplo — DTO tipado com validação simples:
```python
from dataclasses import dataclass

@dataclass
class CreateUserDTO:
    email: str
    name: str
    def validate(self) -> None:
        if "@" not in self.email:
            raise ValueError("Invalid email")
        if not self.name:
            raise ValueError("Name is required")
```

Exemplo — Config Mypy (scripts/mypy.ini):
```ini
[mypy]
python_version = 3.12
disallow_untyped_defs = True
disallow_any_generics = True
no_implicit_optional = True
warn_unused_ignores = True
warn_redundant_casts = True
strict_equality = True
files = src/forgebase/domain
```

Impacto: +Confiabilidade, +IDE assist, -Esforço inicial de anotações.

---

## 2) Observabilidade como API (Decorator track_metrics + LogService)

Objetivo: Fornecer sinais objetivos (tempo, sucesso/falha, contexto) para que agentes possam ajustar estratégias autonomamente.

Exemplo — Decorator de métricas (`src/forgebase/application/decorators/track_metrics.py`):
```python
import time
from functools import wraps
from typing import Callable, Any

def track_metrics(name: str):
    def deco(fn: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            start = time.perf_counter()
            success = True
            try:
                return fn(*args, **kwargs)
            except Exception:
                success = False
                raise
            finally:
                duration_ms = (time.perf_counter() - start) * 1000
                # Aqui integrar com LogService/FeedbackManager
                print(f"[METRIC] {name} duration_ms={duration_ms:.2f} success={success}")
        return wrapper
    return deco
```

Exemplo — LogService simples (`src/forgebase/observability/log_service.py`):
```python
class LogService:
    def info(self, msg: str, **ctx):
        print(f"[INFO] {msg} | {ctx}")
    def error(self, msg: str, **ctx):
        print(f"[ERROR] {msg} | {ctx}")
```

Exemplo — Uso em UseCase:
```python
from forgebase.application.decorators.track_metrics import track_metrics

class CreateUserUseCase(UseCaseBase):
    def __init__(self, repo, logger):
        self.repo = repo
        self.logger = logger

    @track_metrics("create_user")
    def execute(self, dto: CreateUserDTO) -> None:
        self.logger.info("start", email=dto.email)
        dto.validate()
        user = User(None, dto.name, dto.email)
        user.validate()
        self.repo.save(user)
        self.logger.info("done", user_id=user.id)
```

Impacto: +Visibilidade, +ajuste autônomo, -Pequena sobrecarga.

---

## 3) Testes de Contrato para Ports/Repositories

Objetivo: Qualquer implementação concreta cumprir um suite comum, evitando regressões ocultas.

Exemplo — Contract test para RepositoryBase:
```python
import unittest

class RepositoryContractTestMixin:
    RepoClass = None  # set pelo teste concreto
    EntityClass = None

    def make_repo(self):
        return self.RepoClass()

    def make_entity(self, **kw):
        return self.EntityClass(**kw)

    def test_crud_cycle(self):
        repo = self.make_repo()
        e = self.make_entity(name="A")
        repo.save(e)
        self.assertTrue(repo.exists(e.id))
        self.assertIsNotNone(repo.find_by_id(e.id))
        repo.delete(e.id)
        self.assertFalse(repo.exists(e.id))
```

Impacto: +Confiabilidade de adapters, +autonomia para agentes validarem integrações.

---

## 4) Scaffolding & Templates (UseCase/Port/Adapter)

Objetivo: Gerar esqueletos consistentes com docstrings, hooks e testes mínimos.

Exemplo — Template de UseCase (gerado por script em `scripts/scaffold_usecase.py`):
```python
USECASE_TMPL = """
from forgebase.application import UseCaseBase
from forgebase.application.decorators.track_metrics import track_metrics

class {class_name}(UseCaseBase):
    def __init__(self, port, logger):
        self.port = port
        self.logger = logger

    @track_metrics("{metric}")
    def execute(self, input_dto):
        input_dto.validate()
        # TODO: implementar
        return None
"""
```

Impacto: +Velocidade, +padrão, -Pequeno esforço de script.

---

## 5) Property-based Testing (Hypothesis) no Domínio

Objetivo: Cobrir bordas automaticamente, reforçando invariantes de VO/validators.

Exemplo — Validator de range:
```python
from hypothesis import given, strategies as st
from forgebase.domain.validators import in_range

@given(st.floats(min_value=0, max_value=1))
def test_in_range_ok(x):
    in_range(x, 0, 1, "score")  # não deve lançar
```

Impacto: +Cobertura, -Dependência leve.

---

## 6) Guardrails Arquiteturais (import-linter)

Objetivo: Impedir dependências proibidas entre camadas (Clean + Hexagonal).

Exemplo — Config (`scripts/importlinter.ini`):
```ini
[importlinter]
root_package = forgebase

[contracts]
layers =
    domain
    application
    adapters
    infrastructure

[layers.domain]
modules = forgebase.domain

[layers.application]
modules = forgebase.application
imports = forgebase.domain

[layers.adapters]
modules = forgebase.adapters
imports = forgebase.application

[layers.infrastructure]
modules = forgebase.infrastructure
imports = forgebase.application, forgebase.domain
```

Impacto: +Coesão arquitetural, -Precisa ajuste fino de regras.

---

## 7) Saúde de Dependências (Deptry)

Objetivo: Detectar dependências não usadas ou ausentes.

Exemplo — Execução:
```bash
deptry src --exclude tests
```

Impacto: +Higiene do projeto, -Custo baixo.

---

## 8) Descoberta & Catálogo Programático

Objetivo: Agentes listarem rapidamente UseCases/Ports/Adapters disponíveis e suas docstrings.

Exemplo — Script `scripts/discover.py`:
```python
import pkgutil, inspect, json
from forgebase.application import UseCaseBase, PortBase
import forgebase

items = {"usecases": [], "ports": []}
for finder, name, ispkg in pkgutil.walk_packages(forgebase.__path__, forgebase.__name__ + "."):
    m = __import__(name, fromlist=["*"])
    for _, obj in inspect.getmembers(m, inspect.isclass):
        if issubclass(obj, UseCaseBase) and obj is not UseCaseBase:
            items["usecases"].append({"name": obj.__name__, "module": obj.__module__, "doc": (obj.__doc__ or "").strip()})
        if issubclass(obj, PortBase) and obj is not PortBase:
            items["ports"].append({"name": obj.__name__, "module": obj.__module__, "doc": (obj.__doc__ or "").strip()})
print(json.dumps(items, ensure_ascii=False, indent=2))
```

Impacto: +Descoberta, +autonomia, -Baixo custo.

---

## 9) Exemplos End-to-End (examples/)

Objetivo: Caminhos felizes de referência para agentes (CLI → UseCase → Repo JSON → Observabilidade).

Exemplo — `examples/run_translation.py` (esqueleto):
```python
from forgebase.adapters.ai.dummy_translator import DummyTranslator
from forgebase.application.usecases.traduzir_texto import TraduzirTexto
from forgebase.observability.log_service import LogService

translator = DummyTranslator()
logger = LogService()
uc = TraduzirTexto(translator, logger)
print(uc.execute("olá mundo"))
```

Impacto: +Produtividade, -Baixo custo.

---

## 10) Automação de Fluxo (scripts/devtool.py)

Objetivo: Uma CLI única para lint, type-check, tests, discover.

Exemplo — `scripts/devtool.py`:
```python
import argparse, subprocess

def run(cmd: list[str]):
    print("$", " ".join(cmd))
    subprocess.check_call(cmd)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("task", choices=["lint", "fix", "type", "test", "discover"])
    args = ap.parse_args()
    if args.task == "lint":
        run(["bash", "scripts/lint.sh"])
    elif args.task == "fix":
        run(["bash", "scripts/lint.sh", "--fix"])
    elif args.task == "type":
        run(["mypy", "--config-file", "scripts/mypy.ini", "src", "tests"])
    elif args.task == "test":
        run(["pytest", "-q"])
    elif args.task == "discover":
        run(["python", "scripts/discover.py"])

if __name__ == "__main__":
    main()
```

Impacto: +Facilidade de uso por agentes, -Muito baixo custo.

---

## Backlog Prioritizado

P0 — Observabilidade e Contratos
1. Implementar `track_metrics` e `LogService` básicos; integrar em `UseCaseBase` exemplos.
   - Aceite: decorator disponível; logs/metrics visíveis em execuções de exemplo.
2. Adotar Mypy (strict) em `domain/` (config em `scripts/mypy.ini`, hook no pre-commit).
   - Aceite: `bash scripts/typecheck.sh` sem erros no domínio.
3. Criar Contract Tests para `RepositoryBase` e aplicar em JSONRepository.
   - Aceite: JSONRepository passa no suite de contrato.

P1 — Guardrails e Scaffolding
4. Import-linter (config `scripts/importlinter.ini`) com regras de camadas.
   - Aceite: `import-linter` passando nas camadas definidas.
5. Scaffolds: `scripts/scaffold_usecase.py` e `scripts/scaffold_port_adapter.py`.
   - Aceite: geração de arquivos com docstrings e testes mínimos.
6. Discovery: `scripts/discover.py` e comando no `devtool.py`.
   - Aceite: lista JSON com UseCases/Ports.

P2 — Cobertura e Saúde
7. Property-based tests (Hypothesis) para validators/VO.
   - Aceite: pelo menos 3 propriedades principais cobertas.
8. Deptry para higiene de dependências.
   - Aceite: relatório sem erros críticos.
9. Exemplos end-to-end atualizados na pasta `examples/`.
   - Aceite: execução demonstra logs + métricas.

P3 — Automação
10. `scripts/devtool.py` com tarefas (lint, fix, type, test, discover).
    - Aceite: comandos funcionam localmente e via pre-commit opcional.

---

## Observações de Governança
- Não escrever configs na raiz sem aprovação explícita; manter tudo sob `scripts/` ou `docs/`.
- Coordenar com o dev ativo no backlog para evitar conflitos (PRs pequenos por submódulo).
- Cada entrega deve incluir docstrings reST explicando “por quê” e “como medir”.
