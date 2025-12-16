"""
Generic build context.

Maintains state during the build process.

Author: ForgeBase Team
Created: 2025-12
"""

import os
from dataclasses import dataclass, field
from typing import Any, Generic, TypeVar

from forge_base.composition.build_spec import BuildSpecBase
from forge_base.composition.plugin_registry import PluginRegistryBase
from forge_base.domain.exceptions import ConfigurationError

S = TypeVar("S", bound=BuildSpecBase)
R = TypeVar("R", bound=PluginRegistryBase)


@dataclass
class BuildContextBase(Generic[S, R]):
    """
    Build context.

    Maintains state during the build process:
    - Reference to spec
    - Reference to registry
    - Cache of already built objects
    - Environment variable overrides

    The cache allows reusing objects (singleton per build).

    :Example:

        ctx = BuildContextBase(spec=my_spec, registry=my_registry)

        # With environment overrides (useful for tests)
        ctx = ctx.with_env(API_KEY="test-key")
    """

    spec: S
    registry: R
    cache: dict[str, Any] = field(default_factory=dict)
    env_overrides: dict[str, str] = field(default_factory=dict)

    def get(self, path: str, default: Any = None) -> Any:
        """
        Get value from spec by path.

        Supports dot notation: "provider.type", "model.temperature"

        :param path: Path in format "key.subkey.subsubkey"
        :param default: Default value if not found
        :return: Found value or default

        :Example:

            provider_type = ctx.get("provider.type")
            temperature = ctx.get("model.temperature", 0.7)
        """
        spec_dict = self.spec.to_dict()
        keys = path.split(".")
        value: Any = spec_dict

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default

        return value

    def resolve(self, kind: str, type_id: str) -> Any:
        """
        Resolve plugin via registry.

        :param kind: Plugin category
        :param type_id: Type identifier
        :return: Class or factory
        """
        return self.registry.resolve(kind, type_id)

    def get_cached(self, key: str) -> Any | None:
        """
        Get object from cache.

        :param key: Cache key
        :return: Object or None
        """
        return self.cache.get(key)

    def set_cached(self, key: str, value: Any) -> None:
        """
        Store object in cache.

        :param key: Cache key
        :param value: Object to store
        """
        self.cache[key] = value

    def resolve_env(self, env_var: str, required: bool = True) -> str | None:
        """
        Resolve environment variable.

        Precedence order:
        1. env_overrides (passed via with_env or constructor)
        2. os.environ (system)

        :param env_var: Variable name
        :param required: If True, raises error if not defined
        :return: Variable value or None
        :raises ConfigurationError: If required=True and variable doesn't exist
        """
        # 1. Check local overrides (useful for tests)
        if env_var in self.env_overrides:
            return self.env_overrides[env_var]

        # 2. Check system environment
        value = os.environ.get(env_var)

        if value is None and required:
            raise ConfigurationError(
                f"Environment variable '{env_var}' not defined. "
                f"Define it in the system or pass via with_env()."
            )

        return value

    def with_env(self, **env_vars: str) -> "BuildContextBase[S, R]":
        """
        Create new context with additional environment variables.

        Returns a new instance, preserving immutability.
        Useful for tests and programmatic configuration.

        :param env_vars: Environment variables as kwargs
        :return: New context with overrides

        :Example:

            # For tests
            test_ctx = ctx.with_env(
                OPENAI_API_KEY="sk-test-123",
                DATABASE_URL="sqlite:///:memory:"
            )
        """
        new_overrides = {**self.env_overrides, **env_vars}
        return BuildContextBase(
            spec=self.spec,
            registry=self.registry,
            cache=self.cache.copy(),
            env_overrides=new_overrides,
        )

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__} "
            f"spec={self.spec.__class__.__name__} "
            f"cached={len(self.cache)} "
            f"env_overrides={len(self.env_overrides)}>"
        )
