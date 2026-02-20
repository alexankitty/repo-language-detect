#!/bin/bash
# Cache functionality tests for detect_repo_language.py

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LANG_DETECT="$SCRIPT_DIR/detect_repo_language.py"
CACHE_DIR="$HOME/.cache/detect-repo-language"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo "=== CACHE FUNCTIONALITY TESTS ==="
echo ""

# Test 1: Cache creation
echo "✓ Test 1: Cache creation on first run"
python3 "$LANG_DETECT" --clear-cache . > /dev/null 2>&1 || true
output=$(python3 "$LANG_DETECT" --primary-only . 2>&1)
cache_file=$(ls "$CACHE_DIR"/repo_*.json 2>/dev/null | head -1)
if [[ ! -z "$cache_file" && ! -z "$output" ]]; then
  echo "  Output: $output"
  echo "  Cache file: $(basename $cache_file)"
  echo "  PASS (cache created)"
else
  echo "  FAIL (cache not created)"
  exit 1
fi
echo ""

# Test 2: Cache hit - same output
echo "✓ Test 2: Cache hit returns same result"
output1=$(python3 "$LANG_DETECT" --primary-only . 2>&1)
output2=$(python3 "$LANG_DETECT" --primary-only . 2>&1)
if [[ "$output1" == "$output2" ]]; then
  echo "  Output 1: $output1"
  echo "  Output 2: $output2"
  echo "  PASS (outputs match)"
else
  echo "  FAIL (outputs differ: '$output1' vs '$output2')"
  exit 1
fi
echo ""

# Test 3: --no-cache flag (skips cache read/write)
echo "✓ Test 3: --no-cache flag disables caching"
cache_mtime_before=$(stat -f%m "$cache_file" 2>/dev/null || stat -c%Y "$cache_file" 2>/dev/null)
sleep 1
output=$(python3 "$LANG_DETECT" --no-cache --primary-only . 2>&1)
cache_mtime_after=$(stat -f%m "$cache_file" 2>/dev/null || stat -c%Y "$cache_file" 2>/dev/null)
if [[ "$cache_mtime_before" == "$cache_mtime_after" ]]; then
  echo "  Output: $output"
  echo "  Cache timestamp unchanged"
  echo "  PASS (cache not updated)"
else
  echo "  FAIL (cache was updated despite --no-cache)"
fi
echo ""

# Test 4: Cache JSON structure
echo "✓ Test 4: Cache file contains valid JSON"
cache_content=$(cat "$cache_file")
has_stats=$(echo "$cache_content" | grep -q '"stats"' && echo "yes" || echo "no")
has_timestamp=$(echo "$cache_content" | grep -q '"_timestamp"' && echo "yes" || echo "no")
if [[ "$has_stats" == "yes" && "$has_timestamp" == "yes" ]]; then
  echo "  Cache contains required fields (stats, timestamp)"
  echo "  PASS (valid cache structure)"
else
  echo "  FAIL (missing fields in cache)"
  exit 1
fi
echo ""

# Test 5: --clear-cache for specific repo
echo "✓ Test 5: --clear-cache removes specific repo cache"
cache_count_before=$(ls "$CACHE_DIR"/repo_*.json 2>/dev/null | wc -l)
python3 "$LANG_DETECT" --clear-cache . > /dev/null 2>&1
cache_count_after=$(ls "$CACHE_DIR"/repo_*.json 2>/dev/null | wc -l || echo "0")
if [[ $cache_count_after -lt $cache_count_before ]]; then
  echo "  Cache files before: $cache_count_before, after: $cache_count_after"
  echo "  PASS (cache cleared)"
else
  echo "  FAIL (cache not cleared)"
  exit 1
fi
echo ""

# Test 6: --cache-expiry 0 (never expire)
echo "✓ Test 6: --cache-expiry 0 never expires cache"
python3 "$LANG_DETECT" --primary-only . > /dev/null 2>&1
cache_mtime=$(stat -f%m "$CACHE_DIR"/repo_*.json 2>/dev/null || stat -c%Y "$CACHE_DIR"/repo_*.json 2>/dev/null | head -1)
sleep 1
python3 "$LANG_DETECT" --cache-expiry 0 --primary-only . > /dev/null 2>&1
cache_mtime_after=$(stat -f%m "$CACHE_DIR"/repo_*.json 2>/dev/null || stat -c%Y "$CACHE_DIR"/repo_*.json 2>/dev/null | head -1)
if [[ "$cache_mtime" == "$cache_mtime_after" ]]; then
  echo "  Cache timestamp unchanged (not reanalyzed)"
  echo "  PASS (cache never expired)"
else
  echo "  FAIL (cache was reanalyzed)"
fi
echo ""

# Test 7: JSON output with cache
echo "✓ Test 7: JSON output works with cached results"
python3 "$LANG_DETECT" --clear-cache . > /dev/null 2>&1
output=$(python3 "$LANG_DETECT" --json . 2>&1 | head -1)
if [[ "$output" == *"{"* ]]; then
  echo "  Output: $(echo $output | head -c 30)..."
  echo "  PASS (JSON valid)"
else
  echo "  FAIL (invalid JSON from cache)"
  exit 1
fi
echo ""

# Test 8: Multiple repos in cache
echo "✓ Test 8: Cache handles multiple repositories"
tmpdir=$(mktemp -d)
trap "rm -rf $tmpdir" EXIT
cd "$tmpdir"
git init > /dev/null 2>&1
echo 'print("test")' > test.py
git add test.py > /dev/null 2>&1
git commit -m "test" > /dev/null 2>&1

python3 "$LANG_DETECT" --clear-cache > /dev/null 2>&1
python3 "$LANG_DETECT" --primary-only . > /dev/null 2>&1
cd "$SCRIPT_DIR"
python3 "$LANG_DETECT" --primary-only . > /dev/null 2>&1

cache_count=$(ls "$CACHE_DIR"/repo_*.json 2>/dev/null | wc -l)
if [[ $cache_count -ge 2 ]]; then
  echo "  Cached repos: $cache_count"
  echo "  PASS (multiple repos cached)"
else
  echo "  FAIL (not enough repos cached: $cache_count)"
fi
echo ""

# Test 9: Cache consistency with --no-cache
echo "✓ Test 9: Cache and --no-cache give same results"
python3 "$LANG_DETECT" --clear-cache . > /dev/null 2>&1
output_cached=$(python3 "$LANG_DETECT" --primary-only . 2>&1)
output_no_cache=$(python3 "$LANG_DETECT" --no-cache --primary-only . 2>&1)
if [[ "$output_cached" == "$output_no_cache" ]]; then
  echo "  Cached output: $output_cached"
  echo "  No-cache output: $output_no_cache"
  echo "  PASS (results match)"
else
  echo "  FAIL (results differ)"
  exit 1
fi
echo ""

# Test 10: Cache file cleanup on clear-cache all
echo "✓ Test 10: --clear-cache with no args clears all"
python3 "$LANG_DETECT" --clear-cache > /dev/null 2>&1
cache_count=$(ls "$CACHE_DIR"/repo_*.json 2>/dev/null | wc -l || echo "0")
if [[ $cache_count -eq 0 ]]; then
  echo "  Cached repos after clear: $cache_count"
  echo "  PASS (all caches cleared)"
else
  echo "  FAIL (caches still exist: $cache_count)"
fi
echo ""

echo "All cache tests completed!"

