"""
ForgeBase Developer Tools.

Python APIs for AI agents and programmatic access to development tools.
Provides structured, machine-readable interfaces for scaffolding, testing,
quality checking, and component discovery.

Usage for AI Agents:
    from forgebase.dev.api import QualityChecker, ScaffoldGenerator

    # Check code quality
    checker = QualityChecker()
    results = checker.run_all()

    # Generate boilerplate
    generator = ScaffoldGenerator()
    code = generator.create_usecase("CreateOrder")

Author: ForgeBase Development Team
Created: 2025-11-04
"""
