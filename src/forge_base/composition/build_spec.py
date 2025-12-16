"""
Generic declarative specification.

Defines WHAT should be built, not HOW.
Supports YAML, JSON, and TOML as input formats.

Author: ForgeBase Team
Created: 2025-12
"""

import json
import tomllib
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, TypeVar

import yaml

T = TypeVar("T", bound="BuildSpecBase")


@dataclass
class BuildSpecBase(ABC):
    """
    Declarative specification for building objects.

    Defines WHAT should be built, not HOW.
    The Builder is responsible for interpreting the spec.

    Subclasses must define project-specific fields.

    :Example:

        @dataclass
        class LLMBuildSpec(BuildSpecBase):
            agent: dict = field(default_factory=dict)
            provider: dict = field(default_factory=dict)
            model: dict = field(default_factory=dict)

        spec = LLMBuildSpec.from_file("config.yaml")
    """

    # Common fields for all projects
    metadata: dict[str, Any] = field(default_factory=dict)
    observability: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_file(cls: type[T], path: str | Path) -> T:
        """
        Load spec by detecting format from extension.

        Supported formats: .yaml, .yml, .json, .toml

        :param path: File path
        :return: Spec instance
        :raises ValueError: If format not supported
        :raises FileNotFoundError: If file doesn't exist
        """
        path = Path(path)

        if not path.exists():
            raise FileNotFoundError(f"Spec file not found: {path}")

        suffix = path.suffix.lower()

        loaders: dict[str, Any] = {
            ".yaml": cls.from_yaml,
            ".yml": cls.from_yaml,
            ".json": cls.from_json,
            ".toml": cls.from_toml,
        }

        if suffix not in loaders:
            supported = ", ".join(loaders.keys())
            raise ValueError(f"Format '{suffix}' not supported. Use: {supported}")

        return loaders[suffix](path)

    @classmethod
    def from_yaml(cls: type[T], path: str | Path) -> T:
        """
        Load spec from YAML file.

        :param path: File path
        :return: Spec instance
        """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f)

        return cls.from_dict(data or {})

    @classmethod
    def from_json(cls: type[T], path: str | Path) -> T:
        """
        Load spec from JSON file.

        :param path: File path
        :return: Spec instance
        """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        with open(path, encoding="utf-8") as f:
            data = json.load(f)

        return cls.from_dict(data)

    @classmethod
    def from_toml(cls: type[T], path: str | Path) -> T:
        """
        Load spec from TOML file.

        Available natively in Python 3.11+.

        :param path: File path
        :return: Spec instance
        """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        with open(path, "rb") as f:
            data = tomllib.load(f)

        return cls.from_dict(data)

    @classmethod
    @abstractmethod
    def from_dict(cls: type[T], data: dict[str, Any]) -> T:
        """
        Create spec from dictionary.

        Must be implemented by subclasses.

        :param data: Dictionary with spec data
        :return: Spec instance
        """
        pass

    @abstractmethod
    def to_dict(self) -> dict[str, Any]:
        """
        Serialize spec to dictionary.

        Must be implemented by subclasses.
        """
        pass

    def to_yaml(self) -> str:
        """Serialize to YAML string."""
        return yaml.dump(self.to_dict(), default_flow_style=False, allow_unicode=True)

    def to_json(self, indent: int = 2) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    @abstractmethod
    def validate(self) -> None:
        """
        Validate the spec.

        Should raise ConfigurationError if invalid.

        :raises ConfigurationError: If spec is invalid
        """
        pass

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} metadata={self.metadata}>"
