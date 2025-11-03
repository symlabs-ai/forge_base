#!/bin/bash
#
# check-architecture.sh - Validate Clean Architecture boundaries
#
# Usage: ./scripts/check-architecture.sh
#
# Runs import-linter to verify that layer dependencies follow Clean Architecture rules:
# - domain: no dependencies on other layers
# - application: depends only on domain
# - infrastructure: depends only on application and domain
# - adapters: depends only on application and domain
#

set -e

echo "🏗️  Checking Clean Architecture boundaries..."
echo "================================================"
echo ""

# Run import-linter
.venv/bin/lint-imports --config .import-linter

echo ""
echo "✅ Architecture boundaries validated!"
