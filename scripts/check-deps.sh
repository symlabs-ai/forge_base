#!/bin/bash
#
# check-deps.sh - Check dependency hygiene with Deptry
#
# Usage: ./scripts/check-deps.sh
#
# Runs deptry to identify:
# - Unused dependencies (declared but not imported)
# - Missing dependencies (imported but not declared)
# - Transitive dependencies (imported indirectly)
# - Development dependencies in production code
#

set -e

echo "🔍 Checking dependency hygiene with Deptry..."
echo "================================================"
echo ""

# Run deptry on the src directory
.venv/bin/deptry src/

echo ""
echo "✅ Dependency hygiene check complete!"
