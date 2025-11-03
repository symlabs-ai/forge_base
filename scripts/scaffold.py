#!/usr/bin/env python3
"""
ForgeBase Scaffolding Tool.

Generates boilerplate code for UseCases, Ports, and Adapters following
ForgeBase conventions and best practices.

Usage:
    python scripts/scaffold.py usecase CreateUser "Creates a new user"
    python scripts/scaffold.py port EmailService "Email sending port"
    python scripts/scaffold.py adapter SMTPEmail "SMTP email adapter"

Author: ForgeBase Development Team
Created: 2025-11-03
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import Literal

ComponentType = Literal["usecase", "port", "adapter"]


class Scaffolder:
    """Generates code from templates."""

    def __init__(self, project_root: Path):
        """
        Initialize scaffolder.

        :param project_root: Project root directory
        """
        self.project_root = project_root
        self.templates_dir = project_root / "scripts" / "templates"
        self.src_dir = project_root / "src" / "forgebase"

    def generate(
        self,
        component_type: ComponentType,
        name: str,
        description: str,
        author: str = "ForgeBase Developer",
    ) -> Path:
        """
        Generate component from template.

        :param component_type: Type of component (usecase, port, adapter)
        :param name: Component name (e.g., "CreateUser")
        :param description: Brief description
        :param author: Author name
        :return: Path to generated file
        """
        if component_type == "usecase":
            return self._generate_usecase(name, description, author)
        if component_type == "port":
            return self._generate_port(name, description, author)
        if component_type == "adapter":
            return self._generate_adapter(name, description, author)
        raise ValueError(f"Unknown component type: {component_type}")

    def _generate_usecase(self, name: str, description: str, author: str) -> Path:
        """Generate UseCase from template."""
        template_path = self.templates_dir / "usecase_template.txt"
        template = template_path.read_text()

        # Convert name to class name (PascalCase + UseCase suffix)
        class_name = self._to_class_name(name)
        if not class_name.endswith("UseCase"):
            class_name += "UseCase"

        # Generate file name (snake_case)
        file_name = self._to_snake_case(class_name) + ".py"
        output_dir = self.src_dir / "application" / "use_cases"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / file_name

        # Fill template
        content = template.format(
            name=name,
            class_name=class_name,
            description=description,
            author=author,
            date=datetime.now().strftime("%Y-%m-%d"),
        )

        output_path.write_text(content)
        return output_path

    def _generate_port(self, name: str, description: str, author: str) -> Path:
        """Generate Port from template."""
        template_path = self.templates_dir / "port_template.txt"
        template = template_path.read_text()

        # Convert name to class name (PascalCase + Port suffix)
        class_name = self._to_class_name(name)
        if not class_name.endswith("Port"):
            class_name += "Port"

        # Generate file name (snake_case)
        file_name = self._to_snake_case(class_name) + ".py"
        output_dir = self.src_dir / "application" / "ports"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / file_name

        # Fill template
        content = template.format(
            name=name,
            class_name=class_name,
            description=description,
            author=author,
            date=datetime.now().strftime("%Y-%m-%d"),
        )

        output_path.write_text(content)
        return output_path

    def _generate_adapter(self, name: str, description: str, author: str) -> Path:
        """Generate Adapter from template."""
        template_path = self.templates_dir / "adapter_template.txt"
        template = template_path.read_text()

        # Convert name to class name (PascalCase + Adapter suffix)
        class_name = self._to_class_name(name)
        if not class_name.endswith("Adapter"):
            class_name += "Adapter"

        # Generate file name (snake_case)
        file_name = self._to_snake_case(class_name) + ".py"
        output_dir = self.src_dir / "adapters"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / file_name

        # Fill template
        content = template.format(
            name=name,
            class_name=class_name,
            description=description,
            author=author,
            date=datetime.now().strftime("%Y-%m-%d"),
            port_name="YourPort",  # Placeholder
            port_class="YourPortClass",  # Placeholder
            implementation_detail="TODO: Specify implementation",
        )

        output_path.write_text(content)
        return output_path

    @staticmethod
    def _to_class_name(name: str) -> str:
        """
        Convert string to PascalCase class name.

        Examples:
            "create user" -> "CreateUser"
            "send_email" -> "SendEmail"
            "HTTPClient" -> "HTTPClient"
        """
        # Split on spaces and underscores
        words = name.replace("_", " ").split()
        # Capitalize each word
        return "".join(word.capitalize() for word in words)

    @staticmethod
    def _to_snake_case(name: str) -> str:
        """
        Convert PascalCase to snake_case.

        Examples:
            "CreateUserUseCase" -> "create_user_use_case"
            "EmailServicePort" -> "email_service_port"
        """
        # Insert underscore before uppercase letters
        result = []
        for i, char in enumerate(name):
            if char.isupper() and i > 0:
                result.append("_")
            result.append(char.lower())
        return "".join(result)


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="ForgeBase scaffolding tool for generating UseCases, Ports, and Adapters",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate a UseCase
  python scripts/scaffold.py usecase CreateUser "Creates a new user in the system"

  # Generate a Port
  python scripts/scaffold.py port EmailService "Port for sending emails"

  # Generate an Adapter
  python scripts/scaffold.py adapter SMTPEmail "SMTP implementation of EmailService"

  # With custom author
  python scripts/scaffold.py usecase ProcessPayment "Processes payment" --author "John Doe"
        """,
    )

    parser.add_argument(
        "type",
        choices=["usecase", "port", "adapter"],
        help="Type of component to generate",
    )
    parser.add_argument("name", help="Component name (e.g., 'CreateUser', 'EmailService')")
    parser.add_argument("description", help="Brief description of the component")
    parser.add_argument(
        "--author",
        default="ForgeBase Developer",
        help="Author name (default: ForgeBase Developer)",
    )

    args = parser.parse_args()

    # Find project root (directory containing pyproject.toml, setup.py, or src/forgebase)
    current = Path.cwd()
    while current != current.parent:
        if (current / "pyproject.toml").exists() or \
           (current / "setup.py").exists() or \
           (current / "src" / "forgebase").exists():
            project_root = current
            break
        current = current.parent
    else:
        print("ERROR: Could not find project root")
        return 1

    # Generate component
    scaffolder = Scaffolder(project_root)
    try:
        output_path = scaffolder.generate(
            component_type=args.type,
            name=args.name,
            description=args.description,
            author=args.author,
        )
        print(f"✅ Generated {args.type}: {output_path}")
        print("\nNext steps:")
        if args.type == "usecase":
            print("  1. Implement business logic in execute() method")
            print("  2. Add validation logic in _validate_input()")
            print("  3. Inject required dependencies in __init__()")
            print("  4. Write tests in tests/unit/application/use_cases/")
        elif args.type == "port":
            print("  1. Define interface methods (replace example_operation)")
            print("  2. Document expected behavior and contracts")
            print("  3. Create adapter implementations")
            print("  4. Write contract tests in tests/contract_tests/")
        elif args.type == "adapter":
            print("  1. Import the port interface this adapter implements")
            print("  2. Implement all port methods")
            print("  3. Add configuration and initialization logic")
            print("  4. Write tests in tests/unit/adapters/")

        return 0

    except Exception as e:
        print(f"ERROR: Failed to generate {args.type}: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
