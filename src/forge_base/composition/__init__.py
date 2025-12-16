"""
Composition module for ForgeBase.

Provides infrastructure for building extensible applications using
the Composition Root pattern. Allows declarative configuration
and plugin-based extensibility.

Key components:
- PluginRegistryBase: Registry for plugins (classes/factories)
- BuildSpecBase: Declarative specification for building objects
- BuildContextBase: Context during build process
- BuilderBase: Composition Root that assembles objects

Philosophy:
    "Quem usa nao cria. Quem cria nao usa."
    (Who uses doesn't create. Who creates doesn't use.)

Example::

    from forge_base.composition import (
        PluginRegistryBase,
        BuildSpecBase,
        BuildContextBase,
        BuilderBase,
    )

    # 1. Define your registry
    class MyRegistry(PluginRegistryBase):
        def register_defaults(self) -> None:
            self.register("service", "api", APIService)

    # 2. Define your spec
    @dataclass
    class MySpec(BuildSpecBase):
        service: dict = field(default_factory=dict)

        @classmethod
        def from_dict(cls, data: dict) -> "MySpec":
            return cls(service=data.get("service", {}))

        def to_dict(self) -> dict:
            return {"service": self.service}

        def validate(self) -> None:
            if not self.service.get("type"):
                raise ConfigurationError("service.type required")

    # 3. Define your builder
    class MyBuilder(BuilderBase[MySpec, MyRegistry, BuildContextBase, Service]):
        def create_registry(self) -> MyRegistry:
            return MyRegistry()

        def create_context(self, spec: MySpec) -> BuildContextBase:
            return BuildContextBase(spec=spec, registry=self.registry)

        def build(self, spec: MySpec) -> Service:
            spec.validate()
            ctx = self.create_context(spec)
            service_cls = ctx.resolve("service", ctx.get("service.type"))
            return service_cls()

    # 4. Use it
    builder = MyBuilder()
    service = builder.build_from_file("config.yaml", MySpec)

Author: ForgeBase Team
Created: 2025-12
"""

from forge_base.composition.build_context import BuildContextBase
from forge_base.composition.build_spec import BuildSpecBase
from forge_base.composition.builder import BuilderBase
from forge_base.composition.plugin_registry import PluginRegistryBase
from forge_base.composition.protocols import LoggerProtocol, MetricsProtocol

__all__ = [
    # Protocols
    "LoggerProtocol",
    "MetricsProtocol",
    # Core classes
    "PluginRegistryBase",
    "BuildSpecBase",
    "BuildContextBase",
    "BuilderBase",
]
