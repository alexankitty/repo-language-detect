# Test Suite

This folder contains automated tests for `detect_repo_language.py`.

## Running Tests

### Run all tests
```bash
bash test_all.sh
```

### Run specific test suite
```bash
bash test_basic.sh          # Basic functionality tests
bash test_prefix.sh         # Prefix option tests
bash test_git_detection.sh  # Git repository detection
bash test_languages.sh      # Language configuration loading
bash test_cache.sh          # Caching functionality tests
```

## Test Files

- **test_basic.sh** - Tests core functionality:
  - Primary-only output
  - Glyph display
  - JSON output
  - Full analysis mode

- **test_prefix.sh** - Tests the `--prefix` option:
  - Text prefixes
  - Icon/emoji prefixes
  - Prefix with glyph combination
  - Prefix with other modes

- **test_git_detection.sh** - Tests git repository detection:
  - Git repository detection
  - Non-git directory handling
  - Silent exit behavior

- **test_languages.sh** - Tests language configuration:
  - Language loading count
  - Template file exclusion
  - Glyph availability

- **test_cache.sh** - Tests caching functionality:
  - Cache creation on first run
  - Cache hit/read on subsequent runs
  - `--no-cache` flag behavior
  - Cache JSON structure validation
  - `--clear-cache` for specific repos
  - `--cache-expiry` settings (0 = never expire)
  - Multiple repository caching
  - Cache consistency

- **test_all.sh** - Master test runner that executes all test suites

## Quick Start

After making changes to the script, run the full test suite:

```bash
cd tests
bash test_all.sh
```

Or run specific tests to validate particular features:

```bash
bash test_prefix.sh   # After modifying prefix functionality
bash test_languages.sh  # After adding new language definitions
```

## Adding New Tests

Create a new `test_<feature>.sh` file in this directory:

```bash
#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$SCRIPT_DIR"

echo "=== FEATURE TESTS ==="
echo ""

echo "✓ Test 1: Description"
output=$(python3 detect_repo_language.py <args> . 2>&1 || true)
echo "  Output: $output"
[[ <condition> ]] && echo "  PASS" || echo "  FAIL"
echo ""

echo "All feature tests completed!"
```

The `test_all.sh` script will automatically discover and run it.

## Notes

- All tests use simple bash scripts for easy modification and debugging
- Tests are designed to be quick (~1s total for full suite)
- Each test is independent and can be run in any order
- Tests handle edge cases like non-git directories gracefully
