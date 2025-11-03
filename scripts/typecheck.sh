#!/bin/bash
#
# Type checking script for ForgeBase
# Uses mypy with strict configuration
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

echo "🔍 Running type checker (mypy)..."
echo "Config: scripts/mypy.ini"
echo "Scope: domain/ + application/"
echo ""

# Run mypy with config
mypy --config-file scripts/mypy.ini

echo ""
echo "✅ Type checking passed!"
