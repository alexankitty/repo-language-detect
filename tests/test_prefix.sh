#!/bin/bash
# Tests for the --prefix option

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$SCRIPT_DIR"
export PYTHONPATH="$SCRIPT_DIR/src:$PYTHONPATH"

echo "=== PREFIX OPTION TESTS ==="
echo ""

echo "✓ Test 1: Text prefix"
output=$(python3 -m detect_repo_language --primary-only --prefix "Language: " . 2>&1 || true)
echo "  Output: $output"
[[ "$output" == "Language: "* ]] && echo "  PASS" || echo "  FAIL"
echo ""

echo "✓ Test 2: Icon prefix"
output=$(python3 -m detect_repo_language --primary-only --prefix "󱔎 " . 2>&1 || true)
echo "  Output: $output"
[[ "$output" == "󱔎 "* ]] && echo "  PASS" || echo "  FAIL"
echo ""

echo "✓ Test 3: Emoji prefix"
output=$(python3 -m detect_repo_language --primary-only --prefix "📝 " . 2>&1 || true)
echo "  Output: $output"
[[ "$output" == "📝 "* ]] && echo "  PASS" || echo "  FAIL"
echo ""

echo "✓ Test 4: Prefix with glyph"
output=$(python3 -m detect_repo_language --primary-only --prefix ">>> " --with-glyph . 2>&1 || true)
echo "  Output: $output"
[[ "$output" == ">>> "* ]] && echo "  PASS" || echo "  FAIL"
echo ""

echo "✓ Test 5: Prefix without --primary-only (should not affect full output)"
output=$(python3 -m detect_repo_language --prefix "test: " . 2>&1 | grep -E "^=|Repository" | head -1 || true)
[[ "$output" == *"="* ]] && echo "  Full analysis unaffected: PASS" || echo "  FAIL: $output"
echo ""

echo "All prefix tests completed!"
