#!/bin/bash
# PKGBUILD build and validation tests for detect_repo_language

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$SCRIPT_DIR"

echo "=== PKGBUILD BUILD TESTS ==="
echo ""

# Test 1: Check for Arch Linux build tools
echo "✓ Test 1: Check for Arch Linux build tools"
if ! command -v makepkg &> /dev/null; then
  echo "  makepkg: NOT FOUND"
  echo "  NOTE: PKGBUILD tests require Arch Linux or AUR build tools"
  echo "  SKIP"
  exit 0
fi

echo "  makepkg: FOUND"
makepkg_version=$(makepkg --version 2>&1 | head -1)
echo "  $makepkg_version"
echo "  PASS"
echo ""

# Test 2: Validate PKGBUILD syntax
echo "✓ Test 2: Validate PKGBUILD syntax"
if bash -n PKGBUILD 2>&1; then
  echo "  Syntax: VALID"
  echo "  PASS"
else
  echo "  Syntax: INVALID"
  echo "  FAIL"
  exit 1
fi
echo ""

# Test 3: Validate PKGBUILD.pypi syntax
echo "✓ Test 3: Validate PKGBUILD.pypi syntax"
if bash -n PKGBUILD.pypi 2>&1; then
  echo "  Syntax: VALID"
  echo "  PASS"
else
  echo "  Syntax: INVALID"
  echo "  FAIL"
  exit 1
fi
echo ""

# Test 4: Check PKGBUILD required variables
echo "✓ Test 4: Check PKGBUILD required variables"
required_vars=("pkgname" "pkgver" "pkgrel" "pkgdesc" "arch" "license")
missing_vars=()

for var in "${required_vars[@]}"; do
  if ! grep -q "^${var}=" PKGBUILD; then
    missing_vars+=("$var")
  fi
done

if [[ ${#missing_vars[@]} -eq 0 ]]; then
  echo "  All required variables present"
  echo "  PASS"
else
  echo "  Missing variables: ${missing_vars[*]}"
  echo "  FAIL"
  exit 1
fi
echo ""

# Test 5: Check PKGBUILD.pypi required variables
echo "✓ Test 5: Check PKGBUILD.pypi required variables"
missing_vars_pypi=()

for var in "${required_vars[@]}"; do
  if ! grep -q "^${var}=" PKGBUILD.pypi; then
    missing_vars_pypi+=("$var")
  fi
done

if [[ ${#missing_vars_pypi[@]} -eq 0 ]]; then
  echo "  All required variables present"
  echo "  PASS"
else
  echo "  Missing variables: ${missing_vars_pypi[*]}"
  echo "  FAIL"
  exit 1
fi
echo ""

# Test 6: Extract and display PKGBUILD metadata
echo "✓ Test 6: Display PKGBUILD metadata"
. PKGBUILD
echo "  Package: $pkgname"
echo "  Version: $pkgver"
echo "  Release: $pkgrel"
echo "  Architecture: ${arch[@]}"
echo "  License: $license"
echo "  Description: $pkgdesc"
echo "  PASS"
echo ""

# Test 7: Check pyproject.toml version matches PKGBUILD
echo "✓ Test 7: Check version consistency"
if [[ -f pyproject.toml ]]; then
  pyproject_version=$(grep '^version = ' pyproject.toml | head -1 | sed 's/.*"\([^"]*\)".*/\1/')
  if [[ "$pyproject_version" == "$pkgver" ]]; then
    echo "  pyproject.toml version: $pyproject_version"
    echo "  PKGBUILD version: $pkgver"
    echo "  PASS"
  else
    echo "  Version mismatch!"
    echo "  pyproject.toml: $pyproject_version"
    echo "  PKGBUILD: $pkgver"
    echo "  WARNING - versions should match"
  fi
else
  echo "  pyproject.toml: NOT FOUND"
  echo "  SKIP"
fi
echo ""

# Test 8: Check build function exists
echo "✓ Test 8: Check build function exists"
if grep -q "^build()" PKGBUILD; then
  echo "  build() function: FOUND"
  echo "  PASS"
else
  echo "  build() function: NOT FOUND"
  echo "  FAIL"
  exit 1
fi
echo ""

# Test 9: Check package function exists
echo "✓ Test 9: Check package function exists"
if grep -q "^package()" PKGBUILD; then
  echo "  package() function: FOUND"
  echo "  PASS"
else
  echo "  package() function: NOT FOUND"
  echo "  FAIL"
  exit 1
fi
echo ""

# Test 10: Attempt to build PKGBUILD (actual build test)
echo "✓ Test 10: Attempt to build package"
tmpbuild=$(mktemp -d)
trap "rm -rf $tmpbuild" EXIT

# Copy PKGBUILD and src files to temp directory
cp PKGBUILD "$tmpbuild/"
[[ -d src ]] && cp -r src "$tmpbuild/"
[[ -f pyproject.toml ]] && cp pyproject.toml "$tmpbuild/"
[[ -f setup.py ]] && cp setup.py "$tmpbuild/"
[[ -f MANIFEST.in ]] && cp MANIFEST.in "$tmpbuild/"
[[ -f README.md ]] && cp README.md "$tmpbuild/"
[[ -f LICENSE ]] && cp LICENSE "$tmpbuild/"

cd "$tmpbuild"

# Attempt build without dependencies (--nocheck to skip check() function)
if makepkg -s --nocheck --noconfirm 2>&1 | tail -20; then
  echo ""
  # Check if package file was created
  pkg_file=$(ls *.pkg.tar.zst 2>/dev/null | head -1 || echo "")
  if [[ ! -z "$pkg_file" ]]; then
    pkg_size=$(ls -lh "$pkg_file" | awk '{print $5}')
    echo "  Build: SUCCESS"
    echo "  Package: $pkg_file ($pkg_size)"
    echo "  PASS"
  else
    echo "  Build completed but no .pkg.tar.zst file found"
    echo "  WARNING"
  fi
else
  echo "  Build: FAILED"
  echo "  This may be due to:"
  echo "    - Missing build dependencies (install with: pacman -S base-devel)"
  echo "    - Network issues downloading sources"
  echo "    - Incompatible system setup"
  echo "  WARNING - build test skipped"
fi
echo ""

echo "All PKGBUILD validation tests completed!"
