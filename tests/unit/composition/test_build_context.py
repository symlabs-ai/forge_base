"""Tests for BuildContextBase."""

import os
from dataclasses import dataclass, field
from typing import Any

import pytest

from forge_base.composition.build_context import BuildContextBase
from forge_base.composition.build_spec import BuildSpecBase
from forge_base.composition.plugin_registry import PluginRegistryBase
from forge_base.domain.exceptions import ConfigurationError


@dataclass
class SampleSpec(BuildSpecBase):
    """Sample spec implementation for tests."""

    service: dict[str, Any] = field(default_factory=dict)
    model: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SampleSpec":
        return cls(
            service=data.get("service", {}),
            model=data.get("model", {}),
            metadata=data.get("metadata", {}),
            observability=data.get("observability", {}),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "service": self.service,
            "model": self.model,
            "metadata": self.metadata,
            "observability": self.observability,
        }

    def validate(self) -> None:
        pass


class DummyService:
    """Dummy service for testing."""
    pass


class SampleRegistry(PluginRegistryBase):
    """Sample registry implementation for tests."""

    def register_defaults(self) -> None:
        self.register("service", "dummy", DummyService)


class TestBuildContextBase:
    """Tests for BuildContextBase."""

    def test_get_simple_path(self) -> None:
        """Should get value by simple path."""
        spec = SampleSpec(service={"type": "api"})
        registry = SampleRegistry()
        ctx = BuildContextBase(spec=spec, registry=registry)

        assert ctx.get("service") == {"type": "api"}

    def test_get_nested_path(self) -> None:
        """Should get value by nested path."""
        spec = SampleSpec(
            service={"type": "api"},
            model={"config": {"temperature": 0.7}},
        )
        registry = SampleRegistry()
        ctx = BuildContextBase(spec=spec, registry=registry)

        assert ctx.get("model.config.temperature") == 0.7

    def test_get_with_default(self) -> None:
        """Should return default for missing path."""
        spec = SampleSpec()
        registry = SampleRegistry()
        ctx = BuildContextBase(spec=spec, registry=registry)

        assert ctx.get("nonexistent", "default") == "default"
        assert ctx.get("service.nonexistent", 42) == 42

    def test_get_missing_returns_none(self) -> None:
        """Should return None for missing path without default."""
        spec = SampleSpec()
        registry = SampleRegistry()
        ctx = BuildContextBase(spec=spec, registry=registry)

        assert ctx.get("nonexistent") is None

    def test_resolve(self) -> None:
        """Should resolve plugin via registry."""
        spec = SampleSpec()
        registry = SampleRegistry()
        registry.register_defaults()
        ctx = BuildContextBase(spec=spec, registry=registry)

        resolved = ctx.resolve("service", "dummy")
        assert resolved is DummyService

    def test_cache_operations(self) -> None:
        """Should cache and retrieve objects."""
        spec = SampleSpec()
        registry = SampleRegistry()
        ctx = BuildContextBase(spec=spec, registry=registry)

        # Initially empty
        assert ctx.get_cached("my_service") is None

        # Set and get
        service = DummyService()
        ctx.set_cached("my_service", service)
        assert ctx.get_cached("my_service") is service

    def test_resolve_env_from_system(self) -> None:
        """Should resolve from system environment."""
        spec = SampleSpec()
        registry = SampleRegistry()
        ctx = BuildContextBase(spec=spec, registry=registry)

        # Set env var
        os.environ["TEST_VAR_12345"] = "test_value"
        try:
            assert ctx.resolve_env("TEST_VAR_12345") == "test_value"
        finally:
            del os.environ["TEST_VAR_12345"]

    def test_resolve_env_from_overrides(self) -> None:
        """Should resolve from overrides first."""
        spec = SampleSpec()
        registry = SampleRegistry()
        ctx = BuildContextBase(
            spec=spec,
            registry=registry,
            env_overrides={"MY_VAR": "override_value"},
        )

        assert ctx.resolve_env("MY_VAR") == "override_value"

    def test_resolve_env_override_takes_precedence(self) -> None:
        """Override should take precedence over system env."""
        spec = SampleSpec()
        registry = SampleRegistry()

        os.environ["TEST_VAR_OVERRIDE"] = "system_value"
        try:
            ctx = BuildContextBase(
                spec=spec,
                registry=registry,
                env_overrides={"TEST_VAR_OVERRIDE": "override_value"},
            )
            assert ctx.resolve_env("TEST_VAR_OVERRIDE") == "override_value"
        finally:
            del os.environ["TEST_VAR_OVERRIDE"]

    def test_resolve_env_required_missing_raises(self) -> None:
        """Should raise for missing required env var."""
        spec = SampleSpec()
        registry = SampleRegistry()
        ctx = BuildContextBase(spec=spec, registry=registry)

        with pytest.raises(ConfigurationError, match="Environment variable"):
            ctx.resolve_env("NONEXISTENT_VAR_12345")

    def test_resolve_env_optional_missing_returns_none(self) -> None:
        """Should return None for missing optional env var."""
        spec = SampleSpec()
        registry = SampleRegistry()
        ctx = BuildContextBase(spec=spec, registry=registry)

        assert ctx.resolve_env("NONEXISTENT_VAR_12345", required=False) is None

    def test_with_env_creates_new_context(self) -> None:
        """with_env should create new context with overrides."""
        spec = SampleSpec()
        registry = SampleRegistry()
        ctx = BuildContextBase(spec=spec, registry=registry)

        new_ctx = ctx.with_env(API_KEY="test-key", DEBUG="true")

        # Original unchanged
        assert "API_KEY" not in ctx.env_overrides

        # New context has overrides
        assert new_ctx.resolve_env("API_KEY") == "test-key"
        assert new_ctx.resolve_env("DEBUG") == "true"

    def test_with_env_preserves_existing_overrides(self) -> None:
        """with_env should preserve existing overrides."""
        spec = SampleSpec()
        registry = SampleRegistry()
        ctx = BuildContextBase(
            spec=spec,
            registry=registry,
            env_overrides={"EXISTING": "value"},
        )

        new_ctx = ctx.with_env(NEW_VAR="new_value")

        assert new_ctx.resolve_env("EXISTING") == "value"
        assert new_ctx.resolve_env("NEW_VAR") == "new_value"

    def test_with_env_copies_cache(self) -> None:
        """with_env should copy cache to new context."""
        spec = SampleSpec()
        registry = SampleRegistry()
        ctx = BuildContextBase(spec=spec, registry=registry)

        service = DummyService()
        ctx.set_cached("service", service)

        new_ctx = ctx.with_env(VAR="value")
        assert new_ctx.get_cached("service") is service

    def test_repr(self) -> None:
        """Should have meaningful repr."""
        spec = SampleSpec()
        registry = SampleRegistry()
        ctx = BuildContextBase(
            spec=spec,
            registry=registry,
            env_overrides={"VAR": "value"},
        )
        ctx.set_cached("key", "value")

        repr_str = repr(ctx)
        assert "BuildContextBase" in repr_str
        assert "SampleSpec" in repr_str
        assert "cached=1" in repr_str
        assert "env_overrides=1" in repr_str
