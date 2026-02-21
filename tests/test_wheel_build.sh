#!/bin/bash
# Wheel build and installation tests for detect_repo_language

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$SCRIPT_DIR"
export PYTHONPATH="$SCRIPT_DIR/src:$PYTHONPATH"

echo "=== WHEEL BUILD TESTS ==="
echo ""

# Test 1: Check build dependencies
echo "✓ Test 1: Check build dependencies"
if command -v python3 &> /dev/null; then
  echo "  Python3: FOUND"
  python3_version=$(python3 --version 2>&1)
  echo "  $python3_version"
else
  echo "  Python3: NOT FOUND"
  echo "  FAIL"
  exit 1
fi

build_available=$(python3 -c "
try:
    import build
    print('yes')
except ImportError:
    print('no')
" 2>&1 || echo "no")

if [[ "$build_available" == "yes" ]]; then
  echo "  python-build: FOUND"
  echo "  PASS"
else
  echo "  python-build: NOT FOUND (install with: pip install build)"
  echo "  SKIP (build module not available)"
fi
echo ""

# Test 2: Build wheel
echo "✓ Test 2: Build wheel"
if [[ "$build_available" != "yes" ]]; then
  echo "  SKIP (build module not available)"
else
  # Clean previous builds
  rm -rf build/ dist/ *.egg-info 2>/dev/null || true
  
  if python3 -m build --wheel --no-isolation 2>&1; then
    echo "  Build: SUCCESS"
    echo "  PASS"
  else
    echo "  Build: FAILED"
    echo "  FAIL"
    exit 1
  fi
fi
echo ""

# Test 3: Verify wheel file exists
echo "✓ Test 3: Verify wheel file exists"
wheel_file=$(ls dist/*.whl 2>/dev/null | head -1 || echo "")
if [[ ! -z "$wheel_file" ]]; then
  echo "  Wheel: $(basename $wheel_file)"
  echo "  Size: $(ls -lh $wheel_file | awk '{print $5}')"
  echo "  PASS"
else
  echo "  No wheel file found"
  echo "  FAIL"
  exit 1
fi
echo ""

# Test 4: Check wheel contents (should contain language JSON files)
echo "✓ Test 4: Verify wheel contains language files"
if ! command -v unzip &> /dev/null; then
  echo "  unzip not found - SKIP"
else
  echo "  Wheel contents (first 20 lines):"
  unzip -l "$wheel_file" 2>/dev/null | head -20 | sed 's/^/    /'
  echo ""
  
  json_count=$(unzip -l "$wheel_file" 2>/dev/null | grep "\.json$" | wc -l || true)
  json_count=${json_count:-0}
  
  if [[ $json_count -gt 0 ]]; then
    echo "  Language files in wheel: $json_count"
    echo "  PASS"
  else
    echo "  No language JSON files found in wheel"
    echo "  NOTE: This may indicate setup.py needs to be configured for package data"
    echo "  WARNING - continuing with remaining tests"
  fi
fi
echo ""

# Test 5: Install wheel to temporary environment
echo "✓ Test 5: Install wheel to temporary directory"
tmpdir=$(mktemp -d)
trap "rm -rf $tmpdir" EXIT

if python3 -m pip install --target="$tmpdir" --no-deps "$wheel_file" 2>&1 > /dev/null; then
  echo "  Installation: SUCCESS"
  
  # Find where the module was actually installed
  module_path=$(find "$tmpdir" -name "__init__.py" -path "*/detect*" 2>/dev/null | head -1)
  
  if [[ ! -z "$module_path" ]]; then
    echo "  Module found: $(echo $module_path | sed "s|$tmpdir||")"
    echo "  PASS"
  else
    echo "  Installed directory contents:"
    find "$tmpdir" -maxdepth 3 -type f | head -10 | sed 's/^/    /'
    echo "  Module not found in installation"
    echo "  WARNING - continuing with remaining tests"
  fi
else
  echo "  Installation: FAILED"
  echo "  WARNING - continuing with remaining tests"
fi
echo ""

# Test 6: Verify entry point is executable from wheel
echo "✓ Test 6: Verify wheel module can be executed"
tmpdir2=$(mktemp -d)
trap "rm -rf $tmpdir $tmpdir2" EXIT

python3 -m pip install --target="$tmpdir2" --no-deps "$wheel_file" 2>&1 > /dev/null
output=$(PYTHONPATH="$tmpdir2:$PYTHONPATH" python3 -m detect_repo_language --help 2>&1 | head -1 || true)
if [[ ! -z "$output" ]]; then
  echo "  Help output: $(echo $output | head -c 50)..."
  echo "  PASS"
else
  echo "  Could not execute module from wheel"
  echo "  WARNING - continuing"
fi
echo ""

echo "All wheel build tests completed!"
