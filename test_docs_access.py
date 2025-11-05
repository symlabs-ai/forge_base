#!/usr/bin/env python3
"""
Test script to verify documentation is accessible.
"""

import sys
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent / "src"))

from forgebase.dev import get_agent_quickstart, get_documentation_path


def test_agent_quickstart():
    """Test AI Agent Quick Start guide access."""
    print("=" * 60)
    print("Testing get_agent_quickstart()")
    print("=" * 60)

    guide = get_agent_quickstart()

    assert len(guide) > 100, "Guide content is too short"
    assert "ForgeBase AI Agent" in guide, "Guide doesn't contain expected title"
    assert "QualityChecker" in guide, "Guide doesn't mention QualityChecker"

    print(f"✅ Guide loaded successfully ({len(guide)} chars)")
    print("\nFirst 200 characters:")
    print(guide[:200])
    print("\n...")


def test_documentation_path():
    """Test documentation path access."""
    print("\n" + "=" * 60)
    print("Testing get_documentation_path()")
    print("=" * 60)

    docs_path = get_documentation_path()
    print(f"Documentation path: {docs_path}")
    print(f"Exists: {docs_path.exists()}")

    if docs_path.exists():
        print("\nContents:")
        for item in sorted(docs_path.iterdir())[:10]:
            print(f"  - {item.name}")


if __name__ == "__main__":
    try:
        test_agent_quickstart()
        test_documentation_path()
        print("\n" + "=" * 60)
        print("✅ All tests passed!")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
