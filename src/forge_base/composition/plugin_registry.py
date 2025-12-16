"""
Generic plugin registry.

Maps (kind, type_id) to concrete class or factory.
Allows extensibility without modifying existing code.

Author: ForgeBase Team
Created: 2025-12
"""

from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any

# Type aliases for clarity
PluginClass = type
PluginFactory = Callable[..., Any]
PluginEntry = PluginClass | PluginFactory


class PluginRegistryBase(ABC):
    """
    Central extensibility registry.

    Maps (kind, type_id) to concrete class or factory.

    Examples of usage in derived projects:
    - forge_llm: ("provider", "openai") -> OpenAIAdapter
    - forge_db: ("repository", "postgres") -> PostgresRepository
    - forge_api: ("auth", "jwt") -> JWTAuthAdapter

    Subclasses must implement register_defaults() to register
    the default plugins for the project.

    :Example:

        class LLMRegistry(PluginRegistryBase):
            def register_defaults(self) -> None:
                self.register("provider", "openai", OpenAIProvider)
                self.register("provider", "anthropic", AnthropicProvider)

        registry = LLMRegistry()
        provider_cls = registry.resolve("provider", "openai")
        provider = provider_cls(api_key="sk-...")
    """

    def __init__(self) -> None:
        self._registry: dict[str, dict[str, PluginEntry]] = {}

    def register(
        self,
        kind: str,
        type_id: str,
        plugin: PluginEntry,
    ) -> None:
        """
        Register a plugin.

        :param kind: Plugin category (e.g., "provider", "agent", "repository")
        :param type_id: Type identifier (e.g., "openai", "chat", "postgres")
        :param plugin: Class or factory function
        """
        if kind not in self._registry:
            self._registry[kind] = {}
        self._registry[kind][type_id] = plugin

    def unregister(self, kind: str, type_id: str) -> bool:
        """
        Remove a plugin from the registry.

        :param kind: Plugin category
        :param type_id: Type identifier
        :return: True if removed, False if not found
        """
        if kind in self._registry and type_id in self._registry[kind]:
            del self._registry[kind][type_id]
            return True
        return False

    def resolve(self, kind: str, type_id: str) -> PluginEntry:
        """
        Resolve a plugin by kind and type_id.

        :param kind: Plugin category
        :param type_id: Type identifier
        :return: Registered class or factory
        :raises KeyError: If not found
        """
        if kind not in self._registry:
            available_kinds = list(self._registry.keys())
            raise KeyError(
                f"Plugin kind '{kind}' not registered. "
                f"Available kinds: {available_kinds}"
            )

        if type_id not in self._registry[kind]:
            available = list(self._registry[kind].keys())
            raise KeyError(
                f"Plugin '{kind}/{type_id}' not found. "
                f"Available for '{kind}': {available}"
            )

        return self._registry[kind][type_id]

    def resolve_and_instantiate(
        self,
        kind: str,
        type_id: str,
        **kwargs: Any,
    ) -> Any:
        """
        Resolve and instantiate plugin with arguments.

        Convenience method for cases where you want to resolve and create
        the object in a single call.

        :param kind: Plugin category
        :param type_id: Type identifier
        :param kwargs: Arguments for the constructor/factory
        :return: Plugin instance

        :Example:

            provider = registry.resolve_and_instantiate(
                "provider", "openai",
                api_key="sk-...",
                log=log_service,
            )
        """
        plugin = self.resolve(kind, type_id)
        return plugin(**kwargs)

    def list_plugins(self, kind: str) -> "list[str]":
        """
        List plugins in a category.

        :param kind: Plugin category
        :return: List of registered type_ids
        """
        if kind not in self._registry:
            return []
        return [*self._registry[kind].keys()]

    def list_kinds(self) -> "list[str]":
        """
        List all registered categories.

        :return: List of kinds
        """
        return [*self._registry.keys()]

    def is_registered(self, kind: str, type_id: str) -> bool:
        """
        Check if a plugin is registered.

        :param kind: Plugin category
        :param type_id: Type identifier
        :return: True if registered
        """
        return kind in self._registry and type_id in self._registry[kind]

    @abstractmethod
    def register_defaults(self) -> None:
        """
        Register default plugins for the project.

        Must be implemented by subclasses to register
        plugins that come "out of the box" with the project.

        :Example:

            def register_defaults(self) -> None:
                self.register("provider", "openai", OpenAIAdapter)
                self.register("provider", "anthropic", AnthropicAdapter)
                self.register("agent", "chat", ChatAgent)
        """
        pass

    def to_dict(self) -> "dict[str, list[str]]":
        """
        Serialize registry for debug/introspection.

        :return: Dictionary {kind: [type_ids]}
        """
        return {kind: [*plugins.keys()] for kind, plugins in self._registry.items()}

    def __repr__(self) -> str:
        total = sum(len(plugins) for plugins in self._registry.values())
        return f"<{self.__class__.__name__} kinds={len(self._registry)} plugins={total}>"
