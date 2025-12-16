#!/bin/bash
#
# Sync documentation from docs/ to embedded package
#
# This script ensures that the documentation files in the docs/ directory
# are synchronized with the embedded copies in src/forge_base/_docs/
# that get distributed with the package.
#
# Usage:
#   ./scripts/sync_docs.sh
#
# Or use as pre-commit hook (see docs/referencia/acesso-documentacao.md)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DOCS_DIR="$PROJECT_ROOT/src/forge_base/_docs"

echo "📚 Syncing embedded documentation..."

# Create _docs directory if it doesn't exist
mkdir -p "$DOCS_DIR"

# Sync key documentation files for AI agents
cp "$PROJECT_ROOT/docs/agentes-ia/inicio-rapido.md" "$DOCS_DIR/AI_AGENT_QUICK_START.md"
cp "$PROJECT_ROOT/README.md" "$DOCS_DIR/"

echo "✅ Synced files:"
echo "  - docs/agentes-ia/inicio-rapido.md -> AI_AGENT_QUICK_START.md"
echo "  - README.md"

# Verify
if [ ! -f "$DOCS_DIR/AI_AGENT_QUICK_START.md" ]; then
    echo "❌ ERROR: AI_AGENT_QUICK_START.md not found after sync"
    exit 1
fi

if [ ! -f "$DOCS_DIR/README.md" ]; then
    echo "❌ ERROR: README.md not found after sync"
    exit 1
fi

echo ""
echo "✅ Documentation sync complete!"
echo ""
echo "Don't forget to commit the changes in src/forge_base/_docs/"
