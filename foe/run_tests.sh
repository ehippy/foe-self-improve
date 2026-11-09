#!/usr/bin/env bash
set -euo pipefail

# Resolve project root (parent of foe/)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

echo "=== Running Python API tests (pytest) ==="
python3 -m pytest foe/tests/test_api_integration.py -v

echo ""
echo "=== Running JS SPA logic tests (node --test) ==="
node --test foe/tests/test_spa_logic.js

echo ""
echo "ALL TESTS PASSED"
