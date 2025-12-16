"""Tests for BuildSpecBase."""

import json
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pytest
import yaml

from forge_base.composition.build_spec import BuildSpecBase
from forge_base.domain.exceptions import ConfigurationError


@dataclass
class SampleSpec(BuildSpecBase):
    """Sample spec for testing."""

    service: dict[str, Any] = field(default_factory=dict)
    database: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SampleSpec":
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


class TestBuildSpecBase:
    """Tests for BuildSpecBase."""

    def test_from_dict(self) -> None:
        """Should create spec from dict."""
        data = {
            "service": {"type": "api", "port": 8080},
            "database": {"type": "postgres"},
        }
        spec = SampleSpec.from_dict(data)

        assert spec.service["type"] == "api"
        assert spec.service["port"] == 8080
        assert spec.database["type"] == "postgres"

    def test_to_dict(self) -> None:
        """Should serialize to dict."""
        spec = SampleSpec(
            service={"type": "api"},
            database={"type": "postgres"},
        )
        result = spec.to_dict()

        assert result["service"]["type"] == "api"
        assert result["database"]["type"] == "postgres"

    def test_from_yaml(self) -> None:
        """Should load from YAML file."""
        yaml_content = """
service:
  type: api
  port: 8080
database:
  type: postgres
"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as f:
            f.write(yaml_content)
            f.flush()

            spec = SampleSpec.from_yaml(f.name)
            assert spec.service["type"] == "api"
            assert spec.service["port"] == 8080

            Path(f.name).unlink()

    def test_from_json(self) -> None:
        """Should load from JSON file."""
        json_content = {
            "service": {"type": "api", "port": 8080},
            "database": {"type": "postgres"},
        }
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            json.dump(json_content, f)
            f.flush()

            spec = SampleSpec.from_json(f.name)
            assert spec.service["type"] == "api"

            Path(f.name).unlink()

    def test_from_toml(self) -> None:
        """Should load from TOML file."""
        toml_content = """
[service]
type = "api"
port = 8080

[database]
type = "postgres"
"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".toml", delete=False
        ) as f:
            f.write(toml_content)
            f.flush()

            spec = SampleSpec.from_toml(f.name)
            assert spec.service["type"] == "api"
            assert spec.service["port"] == 8080

            Path(f.name).unlink()

    def test_from_file_yaml(self) -> None:
        """Should auto-detect YAML format."""
        yaml_content = "service:\n  type: api"
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as f:
            f.write(yaml_content)
            f.flush()

            spec = SampleSpec.from_file(f.name)
            assert spec.service["type"] == "api"

            Path(f.name).unlink()

    def test_from_file_yml(self) -> None:
        """Should auto-detect .yml format."""
        yaml_content = "service:\n  type: api"
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yml", delete=False
        ) as f:
            f.write(yaml_content)
            f.flush()

            spec = SampleSpec.from_file(f.name)
            assert spec.service["type"] == "api"

            Path(f.name).unlink()

    def test_from_file_unsupported_format(self) -> None:
        """Should raise for unsupported format."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".xml", delete=False
        ) as f:
            f.write("<xml/>")
            f.flush()

            with pytest.raises(ValueError, match="Format '.xml' not supported"):
                SampleSpec.from_file(f.name)

            Path(f.name).unlink()

    def test_from_file_not_found(self) -> None:
        """Should raise for missing file."""
        with pytest.raises(FileNotFoundError):
            SampleSpec.from_file("/nonexistent/path.yaml")

    def test_to_yaml(self) -> None:
        """Should serialize to YAML string."""
        spec = SampleSpec(service={"type": "api"})
        yaml_str = spec.to_yaml()

        # Parse back to verify
        data = yaml.safe_load(yaml_str)
        assert data["service"]["type"] == "api"

    def test_to_json(self) -> None:
        """Should serialize to JSON string."""
        spec = SampleSpec(service={"type": "api"})
        json_str = spec.to_json()

        # Parse back to verify
        data = json.loads(json_str)
        assert data["service"]["type"] == "api"

    def test_validate_valid(self) -> None:
        """Should not raise for valid spec."""
        spec = SampleSpec(service={"type": "api"})
        spec.validate()  # Should not raise

    def test_validate_invalid(self) -> None:
        """Should raise ConfigurationError for invalid spec."""
        spec = SampleSpec(service={})

        with pytest.raises(ConfigurationError, match="service.type is required"):
            spec.validate()

    def test_repr(self) -> None:
        """Should have meaningful repr."""
        spec = SampleSpec(metadata={"version": "1.0"})
        repr_str = repr(spec)
        assert "SampleSpec" in repr_str

    def test_empty_yaml_file(self) -> None:
        """Should handle empty YAML file."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as f:
            f.write("")
            f.flush()

            spec = SampleSpec.from_yaml(f.name)
            assert spec.service == {}

            Path(f.name).unlink()
