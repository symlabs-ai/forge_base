#!/usr/bin/env bash
set -euo pipefail

# Linter runner para ForgeBase usando Ruff, sem escrever nada na raiz.
# Uso:
#   bash scripts/lint.sh           # apenas checa
#   bash scripts/lint.sh --fix     # aplica correções automáticas quando possível

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG="$SCRIPT_DIR/ruff.toml"

if ! command -v ruff >/dev/null 2>&1; then
  echo "[lint] Ruff não encontrado. Instale com: pip install ruff"
  echo "       ou: pip install -r scripts/dev-requirements.txt"
  exit 1
fi

if [[ "${1-}" == "--fix" ]]; then
  shift || true
  echo "[lint] Executando Ruff com --fix"
  ruff check --config "$CONFIG" --fix src tests "$@"
else
  echo "[lint] Executando Ruff (somente checagem)"
  ruff check --config "$CONFIG" src tests "$@"
fi
