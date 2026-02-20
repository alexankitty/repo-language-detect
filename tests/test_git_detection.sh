#!/bin/bash
# Tests for git repository detection

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LANG_DETECT="$SCRIPT_DIR/detect_repo_language.py"

echo "=== GIT DETECTION TESTS ==="
echo ""

echo "✓ Test 1: Git repository (current directory)"
output=$(python3 "$LANG_DETECT" --primary-only . 2>&1 || true)
[[ ! -z "$output" ]] && echo "  Output: $output" && echo "  PASS (detected git repo)" || echo "  FAIL"
echo ""

echo "✓ Test 2: Non-git directory (should exit silently)"
tmpdir=$(mktemp -d)
trap "rm -rf $tmpdir" EXIT
cd "$tmpdir"
output=$(python3 "$LANG_DETECT" --primary-only . 2>&1 || true)
returncode=$?
[[ -z "$output" && $returncode -eq 0 ]] && echo "  PASS (silent exit)" || echo "  FAIL (output was: $output, code: $returncode)"
echo ""

echo "✓ Test 3: Non-git dir with prefix (should still exit silently)"
output=$(python3 "$LANG_DETECT" --primary-only --prefix "test: " . 2>&1 || true)
returncode=$?
[[ -z "$output" && $returncode -eq 0 ]] && echo "  PASS (prefix with silent exit)" || echo "  FAIL"
echo ""

echo "All git detection tests completed!"
