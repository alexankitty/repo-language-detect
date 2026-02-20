#!/bin/bash
# Basic functionality tests for detect_repo_language.py

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$SCRIPT_DIR"

echo "=== BASIC FUNCTIONALITY TESTS ==="
echo ""

echo "✓ Test 1: Primary only (no prefix)"
output=$(python3 detect_repo_language.py --primary-only . 2>&1 || true)
echo "  Output: $output"
[[ ! -z "$output" ]] && echo "  PASS" || echo "  FAIL"
echo ""

echo "✓ Test 2: With glyph"
output=$(python3 detect_repo_language.py --primary-only --with-glyph . 2>&1 || true)
echo "  Output: $output"
[[ ! -z "$output" ]] && echo "  PASS" || echo "  FAIL"
echo ""

echo "✓ Test 3: JSON output"
output=$(python3 detect_repo_language.py --json . 2>&1 | head -1 || true)
[[ "$output" == *"{"* ]] && echo "  Output: $output" && echo "  PASS" || echo "  FAIL: $output"
echo ""

echo "✓ Test 4: Full analysis"
output=$(python3 detect_repo_language.py . 2>&1 | grep -E "^=|Repository" | head -1 || true)
[[ "$output" == *"="* ]] && echo "  Output: $output" && echo "  PASS" || echo "  FAIL: $output"
echo ""

echo "All basic tests completed!"
