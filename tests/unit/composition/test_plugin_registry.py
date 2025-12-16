"""Tests for PluginRegistryBase."""

import pytest

from forge_base.composition.plugin_registry import PluginRegistryBase


class DummyService:
    """Dummy service for testing."""

    def __init__(self, name: str = "default") -> None:
        self.name = name


class AnotherService:
    """Another service for testing."""
    pass


def service_factory(name: str) -> DummyService:
    """Factory function for testing."""
    return DummyService(name=name)


class ConcreteRegistry(PluginRegistryBase):
    """Concrete registry for testing."""

    def register_defaults(self) -> None:
        self.register("service", "dummy", DummyService)
        self.register("service", "another", AnotherService)


class EmptyRegistry(PluginRegistryBase):
    """Registry with no defaults."""

    def register_defaults(self) -> None:
        pass


class TestPluginRegistryBase:
    """Tests for PluginRegistryBase."""

    def test_register_and_resolve(self) -> None:
        """Should register and resolve plugins."""
        registry = EmptyRegistry()
        registry.register("service", "test", DummyService)

        resolved = registry.resolve("service", "test")
        assert resolved is DummyService

    def test_register_factory(self) -> None:
        """Should register factory functions."""
        registry = EmptyRegistry()
        registry.register("service", "factory", service_factory)

        resolved = registry.resolve("service", "factory")
        assert resolved is service_factory

    def test_resolve_unknown_kind_raises(self) -> None:
        """Should raise KeyError for unknown kind."""
        registry = EmptyRegistry()

        with pytest.raises(KeyError, match="Plugin kind 'unknown' not registered"):
            registry.resolve("unknown", "test")

    def test_resolve_unknown_type_raises(self) -> None:
        """Should raise KeyError for unknown type_id."""
        registry = ConcreteRegistry()
        registry.register_defaults()

        with pytest.raises(KeyError, match="Plugin 'service/unknown' not found"):
            registry.resolve("service", "unknown")

    def test_resolve_and_instantiate(self) -> None:
        """Should resolve and instantiate with kwargs."""
        registry = EmptyRegistry()
        registry.register("service", "dummy", DummyService)

        instance = registry.resolve_and_instantiate("service", "dummy", name="test")
        assert isinstance(instance, DummyService)
        assert instance.name == "test"

    def test_unregister(self) -> None:
        """Should unregister plugins."""
        registry = EmptyRegistry()
        registry.register("service", "test", DummyService)

        assert registry.is_registered("service", "test")

        result = registry.unregister("service", "test")
        assert result is True
        assert not registry.is_registered("service", "test")

    def test_unregister_nonexistent(self) -> None:
        """Should return False when unregistering nonexistent plugin."""
        registry = EmptyRegistry()
        result = registry.unregister("service", "nonexistent")
        assert result is False

    def test_list_plugins(self) -> None:
        """Should list plugins in a kind."""
        registry = ConcreteRegistry()
        registry.register_defaults()
        plugins = registry.list_plugins("service")
        assert "dummy" in plugins
        assert "another" in plugins

    def test_list_plugins_empty_kind(self) -> None:
        """Should return empty list for unknown kind."""
        registry = EmptyRegistry()
        plugins = registry.list_plugins("unknown")
        assert plugins == []

    def test_list_kinds(self) -> None:
        """Should list all kinds."""
        registry = ConcreteRegistry()
        registry.register_defaults()
        kinds = registry.list_kinds()
        assert "service" in kinds

    def test_is_registered(self) -> None:
        """Should check if plugin is registered."""
        registry = ConcreteRegistry()
        registry.register_defaults()
        assert registry.is_registered("service", "dummy")
        assert not registry.is_registered("service", "nonexistent")
        assert not registry.is_registered("nonexistent", "dummy")

    def test_to_dict(self) -> None:
        """Should serialize to dict."""
        registry = ConcreteRegistry()
        registry.register_defaults()
        result = registry.to_dict()
        assert "service" in result
        assert "dummy" in result["service"]
        assert "another" in result["service"]

    def test_repr(self) -> None:
        """Should have meaningful repr."""
        registry = ConcreteRegistry()
        registry.register_defaults()
        repr_str = repr(registry)
        assert "ConcreteRegistry" in repr_str
        assert "kinds=1" in repr_str
        assert "plugins=2" in repr_str

    def test_register_defaults_called(self) -> None:
        """register_defaults should be called explicitly."""
        registry = ConcreteRegistry()
        # Defaults not registered yet
        assert not registry.is_registered("service", "dummy")
        # After calling register_defaults
        registry.register_defaults()
        assert registry.is_registered("service", "dummy")
