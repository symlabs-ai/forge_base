"""
Generic Builder (Composition Root).

The only place where objects are created.
Follows the rule: "Who uses doesn't create. Who creates doesn't use."

Author: ForgeBase Team
Created: 2025-12
"""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from forge_base.composition.build_context import BuildContextBase
from forge_base.composition.build_spec import BuildSpecBase
from forge_base.composition.plugin_registry import PluginRegistryBase
from forge_base.composition.protocols import LoggerProtocol, MetricsProtocol

S = TypeVar("S", bound=BuildSpecBase)
R = TypeVar("R", bound=PluginRegistryBase)
C = TypeVar("C", bound=BuildContextBase)  # type: ignore[type-arg]
T = TypeVar("T")  # Type of the final built object


class BuilderBase(ABC, Generic[S, R, C, T]):
    """
    Generic Composition Root.

    The only place where objects are created.
    Follows the rule: "Who uses doesn't create. Who creates doesn't use."

    Responsibilities:
    - Read BuildSpec
    - Create BuildContext
    - Resolve classes via PluginRegistry
    - Instantiate and connect objects
    - Return root object ready for use

    Subclasses must implement:
    - create_registry(): Create project-specific registry
    - create_context(): Create project-specific context
    - build(): Project-specific build logic

    :Example:

        class LLMBuilder(BuilderBase[LLMSpec, LLMRegistry, BuildContextBase, Agent]):
            def create_registry(self) -> LLMRegistry:
                return LLMRegistry()

            def create_context(self, spec: LLMSpec) -> BuildContextBase:
                return BuildContextBase(spec=spec, registry=self.registry)

            def build(self, spec: LLMSpec) -> Agent:
                ctx = self.create_context(spec)
                provider = self._build_provider(ctx)
                return self._build_agent(ctx, provider)
    """

    def __init__(
        self,
        registry: R | None = None,
        log: LoggerProtocol | None = None,
        metrics: MetricsProtocol | None = None,
    ):
        """
        Initialize builder.

        :param registry: Custom registry (optional)
        :param log: Custom logger (optional, uses LogService by default)
        :param metrics: Custom metrics (optional, uses TrackMetrics by default)
        """
        self._registry = registry or self.create_registry()
        self._registry.register_defaults()
        self._log = log or self._create_default_logger()
        self._metrics = metrics or self._create_default_metrics()

    def _create_default_logger(self) -> LoggerProtocol:
        """Create default logger via lazy import."""
        from forge_base.observability.log_service import LogService

        return LogService(service_name=self.__class__.__name__)

    def _create_default_metrics(self) -> MetricsProtocol:
        """Create default metrics via lazy import."""
        from forge_base.observability.track_metrics import TrackMetrics

        return TrackMetrics()

    @property
    def registry(self) -> R:
        """Access to registry."""
        return self._registry

    @property
    def log(self) -> LoggerProtocol:
        """Access to logger."""
        return self._log

    @property
    def metrics(self) -> MetricsProtocol:
        """Access to metrics."""
        return self._metrics

    @abstractmethod
    def create_registry(self) -> R:
        """
        Create registry instance.

        Must be implemented by subclasses.

        :Example:

            def create_registry(self) -> LLMPluginRegistry:
                return LLMPluginRegistry()
        """
        pass

    @abstractmethod
    def create_context(self, spec: S) -> C:
        """
        Create build context.

        Must be implemented by subclasses.

        :Example:

            def create_context(self, spec: LLMBuildSpec) -> BuildContextBase:
                return BuildContextBase(spec=spec, registry=self.registry)
        """
        pass

    @abstractmethod
    def build(self, spec: S) -> T:
        """
        Build root object from spec.

        Must be implemented by subclasses.

        :Example:

            def build(self, spec: LLMBuildSpec) -> AgentBase:
                spec.validate()
                ctx = self.create_context(spec)
                provider = self._build_provider(ctx)
                session = self._build_session(ctx)
                agent = self._build_agent(ctx, provider, session)
                return agent
        """
        pass

    def build_from_file(self, path: str, spec_class: type[S]) -> T:
        """
        Build from file (auto-detects format).

        Supports: .yaml, .yml, .json, .toml

        :param path: File path
        :param spec_class: Spec class for deserialization
        :return: Built object
        """
        spec = spec_class.from_file(path)
        return self.build(spec)

    def build_from_yaml(self, path: str, spec_class: type[S]) -> T:
        """
        Build from YAML file.

        :param path: YAML file path
        :param spec_class: Spec class for deserialization
        :return: Built object
        """
        spec = spec_class.from_yaml(path)
        return self.build(spec)

    def build_from_json(self, path: str, spec_class: type[S]) -> T:
        """
        Build from JSON file.

        :param path: JSON file path
        :param spec_class: Spec class for deserialization
        :return: Built object
        """
        spec = spec_class.from_json(path)
        return self.build(spec)

    def build_from_toml(self, path: str, spec_class: type[S]) -> T:
        """
        Build from TOML file.

        :param path: TOML file path
        :param spec_class: Spec class for deserialization
        :return: Built object
        """
        spec = spec_class.from_toml(path)
        return self.build(spec)

    def build_from_dict(self, data: dict, spec_class: type[S]) -> T:
        """
        Build from dictionary.

        :param data: Dictionary with spec data
        :param spec_class: Spec class for deserialization
        :return: Built object
        """
        spec = spec_class.from_dict(data)
        return self.build(spec)

    def _build_observability(
        self,
        ctx: C,
    ) -> tuple[LoggerProtocol, MetricsProtocol]:
        """
        Build observability services.

        Utility method that can be used by subclasses.
        Uses instances injected in constructor or creates new ones
        based on spec configuration.

        :param ctx: Build context
        :return: Tuple (logger, metrics)
        """
        obs_config = ctx.get("observability", {})

        # If no specific config, use builder defaults
        if not obs_config:
            return self._log, self._metrics

        # Create new based on config
        from forge_base.observability.log_service import LogService
        from forge_base.observability.track_metrics import TrackMetrics

        log = LogService(
            service_name=obs_config.get("service_name", "forge"),
            environment=obs_config.get("environment", "development"),
        )

        if obs_config.get("console_logging", True):
            log.add_console_handler()

        if log_file := obs_config.get("log_file"):
            log.add_file_handler(log_file)

        metrics = TrackMetrics()

        return log, metrics

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} registry={self._registry}>"
