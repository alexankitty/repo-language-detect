#!/bin/bash
# Tests for language configuration loading

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$SCRIPT_DIR"
export PYTHONPATH="$SCRIPT_DIR/src:$PYTHONPATH"

echo "=== LANGUAGE LOADING TESTS ==="
echo ""

echo "✓ Test 1: Count loaded languages"
# Count JSON files in languages directory minus templates
expected_count=$(find "$SCRIPT_DIR/src/detect_repo_language/languages" -name "*.json" ! -name "TEMPLATE*" | wc -l)
count=$(python3 -c "
from detect_repo_language import LANGUAGE_EXTENSIONS, load_language_config
load_language_config()
print(len(LANGUAGE_EXTENSIONS))
" 2>&1 || true)
echo "  Expected languages: $expected_count"
echo "  Loaded languages: $count"
[[ "$count" == "$expected_count" ]] && echo "  PASS" || echo "  FAIL: Expected $expected_count but got $count"
echo ""

echo "✓ Test 2: Verify TEMPLATE.json is excluded"
count=$(python3 -c "
from detect_repo_language import LANGUAGE_EXTENSIONS, load_language_config
load_language_config()
print('TEMPLATE' in LANGUAGE_EXTENSIONS)
" 2>&1 || true)
[[ "$count" == "False" ]] && echo "  TEMPLATE.json excluded: PASS" || echo "  FAIL: $count"
echo ""

echo "✓ Test 3: Verify language glyphs loaded"
glyph=$(python3 -c "
from detect_repo_language import LANGUAGE_GLYPHS, load_language_config
load_language_config()
print(len([g for g in LANGUAGE_GLYPHS.values() if g]))
" 2>&1 || true)
echo "  Languages with glyphs: $glyph"
[[ $glyph -gt 25 ]] && echo "  PASS" || echo "  FAIL"
echo ""

echo "All language loading tests completed!"
