#!/usr/bin/env python3
"""
ForgeBase Developer Toolkit.

Unified CLI for all development tools and workflows. Integrates scaffolding,
discovery, testing, linting, and quality checks into a single interface.

Usage:
    python devtool.py <command> [options]
    python devtool.py --help
    python devtool.py <command> --help

Commands:
    scaffold     Generate boilerplate for UseCases, Ports, Adapters
    discover     Find and catalog all components in the codebase
    test         Run tests (unit, integration, property-based, contract)
    lint         Run linters (ruff, mypy, import-linter)
    check-deps   Check dependency hygiene with deptry
    check-arch   Validate Clean Architecture boundaries
    check-types  Run type checking with mypy
    quality      Run all quality checks (lint + test + deps + arch)

Author: ForgeBase Development Team
Created: 2025-11-03
"""

import subprocess
import sys


def run_command(cmd: list[str], description: str) -> int:
    """
    Run a command and print formatted output.

    :param cmd: Command to run as list
    :param description: Human-readable description
    :return: Exit code
    """
    print(f"\n{'='*60}")
    print(f"🔧 {description}")
    print(f"{'='*60}")
    print(f"$ {' '.join(cmd)}\n")

    result = subprocess.run(cmd)
    return result.returncode


def scaffold(args: list[str]) -> int:
    """Run scaffolding tool."""
    cmd = [sys.executable, "scripts/scaffold.py"] + args
    return run_command(cmd, "Generating boilerplate code")


def discover(args: list[str]) -> int:
    """Run discovery tool."""
    cmd = [sys.executable, "scripts/discover.py"] + args
    return run_command(cmd, "Discovering components")


def test(args: list[str]) -> int:
    """Run tests."""
    if not args:
        # Default: run all tests
        cmd = [sys.executable, "-m", "pytest", "tests/", "-v"]
    elif args[0] == "unit":
        cmd = [sys.executable, "-m", "pytest", "tests/unit/", "-v"]
    elif args[0] == "integration":
        cmd = [sys.executable, "-m", "pytest", "tests/integration/", "-v"]
    elif args[0] == "property":
        cmd = [sys.executable, "-m", "pytest", "tests/property_based/", "-v"]
    elif args[0] == "contract":
        cmd = [sys.executable, "-m", "pytest", "tests/contract_tests/", "-v"]
    else:
        cmd = [sys.executable, "-m", "pytest"] + args

    return run_command(cmd, "Running tests")


def lint(args: list[str]) -> int:
    """Run all linters."""
    exit_code = 0

    # Ruff
    exit_code |= run_command(
        [sys.executable, "-m", "ruff", "check", "src/", "tests/"],
        "Linting with Ruff"
    )

    # Mypy
    exit_code |= run_command(
        [sys.executable, "-m", "mypy", "--config-file", "scripts/mypy.ini"],
        "Type checking with Mypy"
    )

    # Import-linter
    exit_code |= run_command(
        [".venv/bin/lint-imports", "--config", ".import-linter"],
        "Checking architecture with import-linter"
    )

    return exit_code


def check_deps(args: list[str]) -> int:
    """Check dependency hygiene."""
    cmd = [".venv/bin/deptry", "src/"]
    return run_command(cmd, "Checking dependency hygiene")


def check_arch(args: list[str]) -> int:
    """Check Clean Architecture boundaries."""
    cmd = [".venv/bin/lint-imports", "--config", ".import-linter"]
    return run_command(cmd, "Validating Clean Architecture boundaries")


def check_types(args: list[str]) -> int:
    """Run type checking."""
    cmd = [sys.executable, "-m", "mypy", "--config-file", "scripts/mypy.ini"]
    return run_command(cmd, "Type checking with Mypy")


def quality(args: list[str]) -> int:
    """Run all quality checks."""
    print("\n" + "="*60)
    print("🎯 Running Full Quality Suite")
    print("="*60)

    exit_code = 0

    # 1. Linting
    print("\n📝 Phase 1: Linting")
    exit_code |= lint([])

    # 2. Type checking (already in lint, but emphasize)
    print("\n🔍 Phase 2: Type Safety")
    exit_code |= check_types([])

    # 3. Architecture
    print("\n🏗️  Phase 3: Architecture")
    exit_code |= check_arch([])

    # 4. Dependencies
    print("\n📦 Phase 4: Dependencies")
    try:
        exit_code |= check_deps([])
    except Exception:
        print("⚠️  Deptry check skipped (may need configuration)")

    # 5. Tests
    print("\n🧪 Phase 5: Testing")
    exit_code |= test(["-q"])

    # Summary
    print("\n" + "="*60)
    if exit_code == 0:
        print("✅ All quality checks PASSED!")
    else:
        print("❌ Some quality checks FAILED. See output above.")
    print("="*60 + "\n")

    return exit_code


def main() -> int:
    """Main entry point."""
    if len(sys.argv) < 2:
        print(__doc__)
        return 1

    command = sys.argv[1]
    args = sys.argv[2:]

    commands = {
        "scaffold": scaffold,
        "discover": discover,
        "test": test,
        "lint": lint,
        "check-deps": check_deps,
        "check-arch": check_arch,
        "check-types": check_types,
        "quality": quality,
    }

    if command in ["--help", "-h", "help"]:
        print(__doc__)
        return 0

    if command not in commands:
        print(f"Unknown command: {command}")
        print(f"Available commands: {', '.join(commands.keys())}")
        print("Run 'python devtool.py --help' for more information")
        return 1

    return commands[command](args)


if __name__ == "__main__":
    sys.exit(main())
