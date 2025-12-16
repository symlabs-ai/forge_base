"""Tests for BuilderBase."""

import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pytest

from forge_base.composition.build_context import BuildContextBase
from forge_base.composition.build_spec import BuildSpecBase
from forge_base.composition.builder import BuilderBase
from forge_base.composition.plugin_registry import PluginRegistryBase
from forge_base.composition.protocols import LoggerProtocol, MetricsProtocol

# Test implementations


@dataclass
class SampleSpec(BuildSpecBase):
    """Test spec implementation."""

    service: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SampleSpec":
        return cls(
            service=data.get("service", {}),
            metadata=data.get("metadata", {}),
            observability=data.get("observability", {}),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "service": self.service,
            "metadata": self.metadata,
            "observability": self.observability,
        }

    def validate(self) -> None:
        pass


class DummyService:
    """Dummy service for testing."""

    def __init__(self, name: str = "default") -> None:
        self.name = name


class SampleRegistry(PluginRegistryBase):
    """Test registry implementation."""

    def register_defaults(self) -> None:
        self.register("service", "dummy", DummyService)


class FakeLogger:
    """Fake logger for testing."""

    def __init__(self) -> None:
        self.messages: list[tuple[str, str]] = []

    def info(self, message: str, **kwargs) -> None:
        self.messages.append(("info", message))

    def warning(self, message: str, **kwargs) -> None:
        self.messages.append(("warning", message))

    def error(self, message: str, **kwargs) -> None:
        self.messages.append(("error", message))

    def debug(self, message: str, **kwargs) -> None:
        self.messages.append(("debug", message))


class FakeMetrics:
    """Fake metrics for testing."""

    def __init__(self) -> None:
        self.counters: dict[str, int] = {}

    def increment(self, name: str, value: int = 1, **tags) -> None:
        self.counters[name] = self.counters.get(name, 0) + value

    def timing(self, name: str, value: float, **tags) -> None:
        pass


class SampleBuilder(BuilderBase[SampleSpec, SampleRegistry, BuildContextBase, DummyService]):
    """Sample builder implementation for testing."""

    def create_registry(self) -> SampleRegistry:
        return SampleRegistry()

    def create_context(self, spec: SampleSpec) -> BuildContextBase:
        return BuildContextBase(spec=spec, registry=self.registry)

    def build(self, spec: SampleSpec) -> DummyService:
        spec.validate()
        ctx = self.create_context(spec)
        service_type = ctx.get("service.type", "dummy")
        service_cls = ctx.resolve("service", service_type)
        name = ctx.get("service.name", "default")
        return service_cls(name=name)


class SampleBuilderBase:
    """Tests for BuilderBase."""

    def test_init_creates_registry(self) -> None:
        """Should create registry on init."""
        builder = SampleBuilder()
        assert builder.registry is not None
        assert isinstance(builder.registry, SampleRegistry)

    def test_init_with_custom_registry(self) -> None:
        """Should use custom registry if provided."""
        custom_registry = SampleRegistry()
        builder = SampleBuilder(registry=custom_registry)
        assert builder.registry is custom_registry

    def test_init_with_custom_logger(self) -> None:
        """Should use custom logger if provided."""
        fake_log = FakeLogger()
        builder = SampleBuilder(log=fake_log)
        assert builder.log is fake_log

    def test_init_with_custom_metrics(self) -> None:
        """Should use custom metrics if provided."""
        fake_metrics = FakeMetrics()
        builder = SampleBuilder(metrics=fake_metrics)
        assert builder.metrics is fake_metrics

    def test_build(self) -> None:
        """Should build object from spec."""
        builder = SampleBuilder()
        spec = SampleSpec(service={"type": "dummy", "name": "test"})

        result = builder.build(spec)

        assert isinstance(result, DummyService)
        assert result.name == "test"

    def test_build_from_dict(self) -> None:
        """Should build from dictionary."""
        builder = SampleBuilder()
        data = {"service": {"type": "dummy", "name": "from_dict"}}

        result = builder.build_from_dict(data, SampleSpec)

        assert isinstance(result, DummyService)
        assert result.name == "from_dict"

    def test_build_from_yaml(self) -> None:
        """Should build from YAML file."""
        yaml_content = """
service:
  type: dummy
  name: from_yaml
"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as f:
            f.write(yaml_content)
            f.flush()

            builder = SampleBuilder()
            result = builder.build_from_yaml(f.name, SampleSpec)

            assert isinstance(result, DummyService)
            assert result.name == "from_yaml"

            Path(f.name).unlink()

    def test_build_from_json(self) -> None:
        """Should build from JSON file."""
        import json

        json_content = {"service": {"type": "dummy", "name": "from_json"}}
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            json.dump(json_content, f)
            f.flush()

            builder = SampleBuilder()
            result = builder.build_from_json(f.name, SampleSpec)

            assert isinstance(result, DummyService)
            assert result.name == "from_json"

            Path(f.name).unlink()

    def test_build_from_toml(self) -> None:
        """Should build from TOML file."""
        toml_content = """
[service]
type = "dummy"
name = "from_toml"
"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".toml", delete=False
        ) as f:
            f.write(toml_content)
            f.flush()

            builder = SampleBuilder()
            result = builder.build_from_toml(f.name, SampleSpec)

            assert isinstance(result, DummyService)
            assert result.name == "from_toml"

            Path(f.name).unlink()

    def test_build_from_file_auto_detect(self) -> None:
        """Should auto-detect format from extension."""
        yaml_content = """
service:
  type: dummy
  name: auto_detect
"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as f:
            f.write(yaml_content)
            f.flush()

            builder = SampleBuilder()
            result = builder.build_from_file(f.name, SampleSpec)

            assert isinstance(result, DummyService)
            assert result.name == "auto_detect"

            Path(f.name).unlink()

    def test_registry_defaults_registered(self) -> None:
        """Should have default plugins registered."""
        builder = SampleBuilder()
        assert builder.registry.is_registered("service", "dummy")

    def test_repr(self) -> None:
        """Should have meaningful repr."""
        builder = SampleBuilder()
        repr_str = repr(builder)
        assert "SampleBuilder" in repr_str

    def test_logger_protocol_satisfied(self) -> None:
        """Custom logger should satisfy LoggerProtocol."""
        fake_log = FakeLogger()
        assert isinstance(fake_log, LoggerProtocol)

    def test_metrics_protocol_satisfied(self) -> None:
        """Custom metrics should satisfy MetricsProtocol."""
        fake_metrics = FakeMetrics()
        assert isinstance(fake_metrics, MetricsProtocol)


class SampleBuilderObservability:
    """Tests for builder observability integration."""

    def test_build_observability_uses_defaults(self) -> None:
        """Should use default log/metrics when no config."""
        fake_log = FakeLogger()
        fake_metrics = FakeMetrics()
        builder = SampleBuilder(log=fake_log, metrics=fake_metrics)

        spec = SampleSpec()
        ctx = builder.create_context(spec)

        log, metrics = builder._build_observability(ctx)

        # Should return the builder's defaults
        assert log is fake_log
        assert metrics is fake_metrics
