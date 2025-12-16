#!/usr/bin/env python3
"""
ForgeBase Discovery Tool.

Scans the codebase to find and catalog all UseCases, Ports, and Adapters,
providing visibility into the application architecture.

Usage:
    python scripts/discover.py
    python scripts/discover.py --format json
    python scripts/discover.py --type usecase
    python scripts/discover.py --stats

Author: ForgeBase Development Team
Created: 2025-11-03
"""

import argparse
import ast
import json
import sys
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal

ComponentType = Literal["usecase", "port", "adapter"]


@dataclass
class Component:
    """Represents a discovered component."""

    type: ComponentType
    name: str
    module: str
    file_path: str
    line_number: int
    docstring: str | None = None
    base_classes: list[str] | None = None


class ComponentDiscoverer:
    """Discovers components by scanning source files."""

    def __init__(self, project_root: Path):
        """
        Initialize discoverer.

        :param project_root: Project root directory
        """
        self.project_root = project_root
        self.src_dir = project_root / "src" / "forge_base"

    def discover_all(self) -> dict[ComponentType, list[Component]]:
        """
        Discover all components in the codebase.

        :return: Dictionary mapping component type to list of components
        """
        components: dict[ComponentType, list[Component]] = defaultdict(list)

        # Discover UseCases
        usecases_dir = self.src_dir / "application" / "use_cases"
        if usecases_dir.exists():
            for usecase in self._discover_usecases(usecases_dir):
                components["usecase"].append(usecase)

        # Discover Ports
        ports_dir = self.src_dir / "application" / "ports"
        if ports_dir.exists():
            for port in self._discover_ports(ports_dir):
                components["port"].append(port)

        # Discover Adapters
        adapters_dir = self.src_dir / "adapters"
        if adapters_dir.exists():
            for adapter in self._discover_adapters(adapters_dir):
                components["adapter"].append(adapter)

        return dict(components)

    def _discover_usecases(self, directory: Path) -> list[Component]:
        """Discover all UseCase implementations."""
        usecases = []
        for py_file in directory.rglob("*.py"):
            if py_file.name.startswith("_"):
                continue
            usecases.extend(self._extract_usecases(py_file))
        return usecases

    def _discover_ports(self, directory: Path) -> list[Component]:
        """Discover all Port definitions."""
        ports = []
        for py_file in directory.rglob("*.py"):
            if py_file.name.startswith("_"):
                continue
            ports.extend(self._extract_ports(py_file))
        return ports

    def _discover_adapters(self, directory: Path) -> list[Component]:
        """Discover all Adapter implementations."""
        adapters = []
        for py_file in directory.rglob("*.py"):
            if py_file.name.startswith("_"):
                continue
            adapters.extend(self._extract_adapters(py_file))
        return adapters

    def _extract_usecases(self, file_path: Path) -> list[Component]:
        """Extract UseCase classes from a Python file."""
        components = []
        try:
            content = file_path.read_text()
            tree = ast.parse(content)
            module = self._get_module_name(file_path)

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Check if it's a UseCase (inherits from UseCaseBase or ends with UseCase)
                    base_names = [
                        self._get_base_name(base) for base in node.bases
                    ]
                    if any("UseCaseBase" in name for name in base_names) or \
                       node.name.endswith("UseCase"):
                        docstring = ast.get_docstring(node)
                        component = Component(
                            type="usecase",
                            name=node.name,
                            module=module,
                            file_path=str(file_path.relative_to(self.project_root)),
                            line_number=node.lineno,
                            docstring=docstring,
                            base_classes=base_names,
                        )
                        components.append(component)
        except Exception as e:
            # Skip files that can't be parsed
            print(f"Warning: Could not parse {file_path}: {e}", file=sys.stderr)

        return components

    def _extract_ports(self, file_path: Path) -> list[Component]:
        """Extract Port interfaces from a Python file."""
        components = []
        try:
            content = file_path.read_text()
            tree = ast.parse(content)
            module = self._get_module_name(file_path)

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Check if it's a Port (inherits from ABC and ends with Port)
                    base_names = [
                        self._get_base_name(base) for base in node.bases
                    ]
                    if ("ABC" in base_names or any("ABC" in name for name in base_names)) or \
                       node.name.endswith("Port"):
                        # Check if it has abstract methods
                        has_abstract = any(
                            isinstance(n, ast.FunctionDef) and
                            any(
                                isinstance(dec, ast.Name) and dec.id == "abstractmethod"
                                for dec in n.decorator_list
                            )
                            for n in node.body
                        )
                        if has_abstract or node.name.endswith("Port"):
                            docstring = ast.get_docstring(node)
                            component = Component(
                                type="port",
                                name=node.name,
                                module=module,
                                file_path=str(file_path.relative_to(self.project_root)),
                                line_number=node.lineno,
                                docstring=docstring,
                                base_classes=base_names,
                            )
                            components.append(component)
        except Exception as e:
            print(f"Warning: Could not parse {file_path}: {e}", file=sys.stderr)

        return components

    def _extract_adapters(self, file_path: Path) -> list[Component]:
        """Extract Adapter implementations from a Python file."""
        components = []
        try:
            content = file_path.read_text()
            tree = ast.parse(content)
            module = self._get_module_name(file_path)

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and node.name.endswith("Adapter"):
                    # Check if it's an Adapter (ends with Adapter)
                    base_names = [
                        self._get_base_name(base) for base in node.bases
                    ]
                    docstring = ast.get_docstring(node)
                    component = Component(
                        type="adapter",
                        name=node.name,
                        module=module,
                        file_path=str(file_path.relative_to(self.project_root)),
                        line_number=node.lineno,
                        docstring=docstring,
                        base_classes=base_names,
                    )
                    components.append(component)
        except Exception as e:
            print(f"Warning: Could not parse {file_path}: {e}", file=sys.stderr)

        return components

    def _get_module_name(self, file_path: Path) -> str:
        """Convert file path to Python module name."""
        relative = file_path.relative_to(self.project_root)
        parts = list(relative.parts)

        # Remove 'src' if present
        if parts[0] == "src":
            parts = parts[1:]

        # Remove .py extension
        if parts[-1].endswith(".py"):
            parts[-1] = parts[-1][:-3]

        return ".".join(parts)

    @staticmethod
    def _get_base_name(base: ast.expr) -> str:
        """Extract base class name from AST node."""
        if isinstance(base, ast.Name):
            return base.id
        if isinstance(base, ast.Attribute):
            return base.attr
        if isinstance(base, ast.Subscript):
            if isinstance(base.value, ast.Name):
                return base.value.id
            if isinstance(base.value, ast.Attribute):
                return base.value.attr
        return "Unknown"


def format_text(components: dict[ComponentType, list[Component]]) -> str:
    """Format components as human-readable text."""
    lines = []
    lines.append("=" * 60)
    lines.append("ForgeBase Component Discovery")
    lines.append("=" * 60)
    lines.append("")

    total = sum(len(comps) for comps in components.values())
    lines.append(f"Total Components: {total}")
    lines.append("")

    for comp_type in ["usecase", "port", "adapter"]:
        comps = components.get(comp_type, [])
        if not comps:
            continue

        lines.append(f"\n{comp_type.upper()}S ({len(comps)})")
        lines.append("-" * 60)

        for comp in sorted(comps, key=lambda c: c.name):
            lines.append(f"\n  {comp.name}")
            lines.append(f"    Module:   {comp.module}")
            lines.append(f"    File:     {comp.file_path}:{comp.line_number}")
            if comp.base_classes:
                lines.append(f"    Bases:    {', '.join(comp.base_classes)}")
            if comp.docstring:
                first_line = comp.docstring.split("\n")[0]
                if len(first_line) > 50:
                    first_line = first_line[:47] + "..."
                lines.append(f"    Doc:      {first_line}")

    return "\n".join(lines)


def format_json(components: dict[ComponentType, list[Component]]) -> str:
    """Format components as JSON."""
    data = {
        comp_type: [asdict(comp) for comp in comps]
        for comp_type, comps in components.items()
    }
    return json.dumps(data, indent=2)


def format_stats(components: dict[ComponentType, list[Component]]) -> str:
    """Format component statistics."""
    lines = []
    lines.append("=" * 60)
    lines.append("ForgeBase Architecture Statistics")
    lines.append("=" * 60)
    lines.append("")

    total = sum(len(comps) for comps in components.values())
    lines.append(f"Total Components:    {total}")
    lines.append(f"  UseCases:          {len(components.get('usecase', []))}")
    lines.append(f"  Ports:             {len(components.get('port', []))}")
    lines.append(f"  Adapters:          {len(components.get('adapter', []))}")
    lines.append("")

    # Calculate ratios
    num_ports = len(components.get("port", []))
    num_adapters = len(components.get("adapter", []))
    if num_ports > 0:
        adapter_per_port = num_adapters / num_ports
        lines.append(f"Adapters per Port:   {adapter_per_port:.2f}")
    lines.append("")

    # Modules with most components
    module_counts: dict[str, int] = defaultdict(int)
    for comps in components.values():
        for comp in comps:
            module_counts[comp.module.split(".")[0]] += 1

    lines.append("Components by Top-Level Module:")
    for module, count in sorted(module_counts.items(), key=lambda x: -x[1])[:5]:
        lines.append(f"  {module}: {count}")

    return "\n".join(lines)


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Discover and catalog ForgeBase components",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--type",
        choices=["usecase", "port", "adapter"],
        help="Filter by component type",
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show architecture statistics instead of listing components",
    )

    args = parser.parse_args()

    # Find project root
    current = Path.cwd()
    while current != current.parent:
        if (current / "pyproject.toml").exists() or \
           (current / "setup.py").exists() or \
           (current / "src" / "forge_base").exists():
            project_root = current
            break
        current = current.parent
    else:
        print("ERROR: Could not find project root", file=sys.stderr)
        return 1

    # Discover components
    discoverer = ComponentDiscoverer(project_root)
    components = discoverer.discover_all()

    # Filter by type if requested
    if args.type:
        components = {args.type: components.get(args.type, [])}

    # Format and print output
    if args.stats:
        output = format_stats(components)
    elif args.format == "json":
        output = format_json(components)
    else:
        output = format_text(components)

    print(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
