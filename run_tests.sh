#!/usr/bin/env bash
set -euo pipefail

echo "=== Running Python API tests ==="
python3 -m pytest -q foe/tests/test_api_integration.py foe/tests/test_spa_logic.py

echo ""
echo "=== Running JS SPA logic tests ==="
node --test foe/tests/test_spa_logic.js

echo ""
echo "ALL TESTS PASSED"
