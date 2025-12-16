# Guia de Composition Root

> "Quem usa, nao cria. Quem cria, nao usa."

O modulo `composition` implementa o padrao **Composition Root** para montagem declarativa de objetos complexos a partir de arquivos de configuracao (YAML, JSON, TOML).

---

## Conceitos Fundamentais

### O Que e Composition Root?

Composition Root e o padrao onde **toda a montagem de objetos** acontece em um unico lugar, separando claramente:

- **Quem cria**: O Builder monta objetos a partir de specs
- **Quem usa**: O restante do codigo recebe objetos prontos

### Componentes do Modulo

| Componente | Responsabilidade |
|------------|------------------|
| `BuildSpecBase` | Especificacao declarativa (YAML/JSON/TOML) |
| `PluginRegistryBase` | Registro de plugins (kind, type_id) -> classe |
| `BuildContextBase` | Contexto de build com cache e env vars |
| `BuilderBase` | Orquestra montagem de objetos |
| `LoggerProtocol` | Protocolo para loggers (baixo acoplamento) |
| `MetricsProtocol` | Protocolo para metricas (baixo acoplamento) |

---

## Instalacao

O modulo `composition` faz parte do ForgeBase:

```python
from forge_base.composition import (
    BuildSpecBase,
    PluginRegistryBase,
    BuildContextBase,
    BuilderBase,
    LoggerProtocol,
    MetricsProtocol,
)
```

---

## Uso Basico

### 1. Definir um BuildSpec

O BuildSpec define a estrutura da sua configuracao:

```python
from dataclasses import dataclass, field
from typing import Any

from forge_base.composition import BuildSpecBase
from forge_base.domain.exceptions import ConfigurationError


@dataclass
class ServiceSpec(BuildSpecBase):
    """Especificacao para criar um servico."""

    service: dict[str, Any] = field(default_factory=dict)
    database: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ServiceSpec":
        return cls(
            service=data.get("service", {}),
            database=data.get("database", {}),
            metadata=data.get("metadata", {}),
            observability=data.get("observability", {}),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "service": self.service,
            "database": self.database,
            "metadata": self.metadata,
            "observability": self.observability,
        }

    def validate(self) -> None:
        if not self.service.get("type"):
            raise ConfigurationError("service.type is required")
```

### 2. Criar um PluginRegistry

O Registry mapeia tipos para classes concretas:

```python
from forge_base.composition import PluginRegistryBase


class DummyService:
    def __init__(self, name: str = "default"):
        self.name = name


class PostgresDB:
    def __init__(self, host: str = "localhost"):
        self.host = host


class ServiceRegistry(PluginRegistryBase):
    """Registry para servicos."""

    def register_defaults(self) -> None:
        # Registrar plugins padrao
        self.register("service", "dummy", DummyService)
        self.register("database", "postgres", PostgresDB)
```

### 3. Implementar um Builder

O Builder orquestra a montagem:

```python
from forge_base.composition import BuilderBase, BuildContextBase


class ServiceBuilder(BuilderBase[ServiceSpec, ServiceRegistry, BuildContextBase, DummyService]):
    """Builder para servicos."""

    def create_registry(self) -> ServiceRegistry:
        return ServiceRegistry()

    def create_context(self, spec: ServiceSpec) -> BuildContextBase:
        return BuildContextBase(spec=spec, registry=self.registry)

    def build(self, spec: ServiceSpec) -> DummyService:
        # Validar spec
        spec.validate()

        # Criar contexto
        ctx = self.create_context(spec)

        # Resolver plugin do registry
        service_type = ctx.get("service.type", "dummy")
        service_cls = ctx.resolve("service", service_type)

        # Criar instancia
        name = ctx.get("service.name", "default")
        return service_cls(name=name)
```

### 4. Usar o Builder

```python
# A partir de dicionario
builder = ServiceBuilder()
service = builder.build_from_dict(
    {"service": {"type": "dummy", "name": "my-service"}},
    ServiceSpec
)

# A partir de YAML
service = builder.build_from_yaml("config.yaml", ServiceSpec)

# A partir de JSON
service = builder.build_from_json("config.json", ServiceSpec)

# A partir de TOML
service = builder.build_from_toml("config.toml", ServiceSpec)

# Auto-detectar formato pela extensao
service = builder.build_from_file("config.yaml", ServiceSpec)
```

---

## Arquivo de Configuracao

### YAML (Recomendado)

```yaml
# config.yaml
service:
  type: dummy
  name: my-service
  port: 8080

database:
  type: postgres
  host: localhost
  port: 5432

metadata:
  version: "1.0.0"
  author: "Team"

observability:
  log_level: info
  metrics_enabled: true
```

### JSON

```json
{
  "service": {
    "type": "dummy",
    "name": "my-service"
  },
  "database": {
    "type": "postgres"
  }
}
```

### TOML

```toml
[service]
type = "dummy"
name = "my-service"

[database]
type = "postgres"
```

---

## Recursos Avancados

### Navegacao por Path (Dot Notation)

O `BuildContext` permite acessar valores aninhados usando notacao de ponto:

```python
ctx = BuildContextBase(spec=spec, registry=registry)

# Acesso simples
ctx.get("service")  # {"type": "dummy", "name": "my-service"}

# Acesso aninhado
ctx.get("service.type")  # "dummy"
ctx.get("service.port")  # 8080

# Com valor default
ctx.get("service.timeout", 30)  # 30 (se nao existir)
```

### Cache de Objetos

O contexto mantem cache para evitar recriacao:

```python
# Primeira vez: cria
if ctx.get_cached("db_connection") is None:
    conn = create_connection()
    ctx.set_cached("db_connection", conn)

# Segunda vez: reutiliza
conn = ctx.get_cached("db_connection")
```

### Variaveis de Ambiente

Resolucao de variaveis de ambiente com precedencia:

```python
# Sistema de prioridades:
# 1. env_overrides (para testes)
# 2. os.environ (sistema)

# Variavel obrigatoria (raise se nao existir)
api_key = ctx.resolve_env("API_KEY")

# Variavel opcional
debug = ctx.resolve_env("DEBUG", required=False)

# Criar novo contexto com overrides (para testes)
test_ctx = ctx.with_env(
    API_KEY="test-key",
    DEBUG="true"
)
```

### Observability via Protocols

O Builder usa Protocols para baixo acoplamento:

```python
from forge_base.composition import LoggerProtocol, MetricsProtocol


class MyLogger:
    """Logger customizado."""

    def info(self, message: str, **kwargs) -> None:
        print(f"INFO: {message}")

    def warning(self, message: str, **kwargs) -> None:
        print(f"WARN: {message}")

    def error(self, message: str, **kwargs) -> None:
        print(f"ERROR: {message}")

    def debug(self, message: str, **kwargs) -> None:
        print(f"DEBUG: {message}")


class MyMetrics:
    """Metricas customizadas."""

    def increment(self, name: str, value: int = 1, **tags) -> None:
        print(f"METRIC: {name} += {value}")

    def timing(self, name: str, value: float, **tags) -> None:
        print(f"TIMING: {name} = {value}ms")


# Usar com Builder
builder = ServiceBuilder(
    log=MyLogger(),
    metrics=MyMetrics()
)
```

---

## Padrao para Apps Derivados

Apps que dependem do ForgeBase podem expor sua propria Discovery API:

```python
# my_app/discovery.py
from forge_base.dev.api import ComponentDiscovery


class MyAppDiscovery(ComponentDiscovery):
    """Discovery para minha aplicacao."""

    def __init__(self):
        # Escanear apenas o pacote instalado
        super().__init__(package_name="my_app")


# Uso por agentes IA
discovery = MyAppDiscovery()
result = discovery.scan_project()

# Ver componentes de composition
print(f"Registries: {len(result.registries)}")
print(f"Builders: {len(result.builders)}")
print(f"Specs: {len(result.specs)}")
```

---

## Exemplo Completo

```python
"""Exemplo completo de uso do modulo composition."""

from dataclasses import dataclass, field
from typing import Any

from forge_base.composition import (
    BuildSpecBase,
    PluginRegistryBase,
    BuildContextBase,
    BuilderBase,
)
from forge_base.domain.exceptions import ConfigurationError


# 1. Servico de dominio
class APIService:
    def __init__(self, name: str, port: int = 8080):
        self.name = name
        self.port = port

    def start(self) -> None:
        print(f"Starting {self.name} on port {self.port}")


# 2. Spec
@dataclass
class APISpec(BuildSpecBase):
    api: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "APISpec":
        return cls(
            api=data.get("api", {}),
            metadata=data.get("metadata", {}),
            observability=data.get("observability", {}),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "api": self.api,
            "metadata": self.metadata,
            "observability": self.observability,
        }

    def validate(self) -> None:
        if not self.api.get("name"):
            raise ConfigurationError("api.name is required")


# 3. Registry
class APIRegistry(PluginRegistryBase):
    def register_defaults(self) -> None:
        self.register("api", "rest", APIService)


# 4. Builder
class APIBuilder(BuilderBase[APISpec, APIRegistry, BuildContextBase, APIService]):
    def create_registry(self) -> APIRegistry:
        return APIRegistry()

    def create_context(self, spec: APISpec) -> BuildContextBase:
        return BuildContextBase(spec=spec, registry=self.registry)

    def build(self, spec: APISpec) -> APIService:
        spec.validate()
        ctx = self.create_context(spec)

        service_cls = ctx.resolve("api", ctx.get("api.type", "rest"))
        return service_cls(
            name=ctx.get("api.name"),
            port=ctx.get("api.port", 8080)
        )


# 5. Uso
if __name__ == "__main__":
    # Criar builder
    builder = APIBuilder()

    # Construir a partir de dict
    api = builder.build_from_dict(
        {"api": {"name": "my-api", "port": 3000}},
        APISpec
    )

    # Usar
    api.start()  # Starting my-api on port 3000
```

---

## Descoberta de Componentes

O `ComponentDiscovery` detecta automaticamente componentes de composition:

```python
from forge_base.dev.api import ComponentDiscovery

discovery = ComponentDiscovery()
result = discovery.scan_project()

# Listar registries
for reg in result.registries:
    print(f"Registry: {reg.name} em {reg.file_path}:{reg.line_number}")

# Listar builders
for builder in result.builders:
    print(f"Builder: {builder.name} em {builder.file_path}:{builder.line_number}")

# Listar specs
for spec in result.specs:
    print(f"Spec: {spec.name} em {spec.file_path}:{spec.line_number}")
```

---

## Boas Praticas

1. **Um Builder por Dominio**: Crie builders especificos para cada dominio (ServiceBuilder, PipelineBuilder, etc.)

2. **Specs Validaveis**: Sempre implemente `validate()` para detectar erros cedo

3. **Defaults Sensiveis**: Registre plugins padrao em `register_defaults()`

4. **Testes com env_overrides**: Use `with_env()` para injetar variaveis em testes

5. **Protocols para Observability**: Use `LoggerProtocol` e `MetricsProtocol` para baixo acoplamento

---

## Proximos Passos

- [Arquitetura](../referencia/arquitetura.md) — Estrutura do framework
- [ForgeProcess](../referencia/forge-process.md) — Ciclo cognitivo completo
- [Receitas](receitas.md) — Padroes e exemplos praticos

---

**"Composicao e o segredo da modularidade."**
