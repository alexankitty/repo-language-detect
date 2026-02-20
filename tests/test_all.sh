#!/bin/bash
# Comprehensive test runner - runs all test suites

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo ""
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║     detect_repo_language.py - Comprehensive Test Suite    ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# Track results
total_tests=0
failed_tests=0

run_test_file() {
    local test_file="$1"
    local test_name=$(basename "$test_file" .sh)
    
    echo "Running: $test_name"
    echo "───────────────────────────────────────────────────────────"
    
    if bash "$test_file"; then
        echo "✓ $test_name completed successfully"
    else
        echo "✗ $test_name failed"
        ((failed_tests++))
    fi
    
    echo ""
}

# Run all test files
for test_file in test_*.sh; do
    if [[ -f "$test_file" && "$test_file" != "test_all.sh" ]]; then
        run_test_file "$test_file"
        ((total_tests++))
    fi
done

# Print summary
echo "═══════════════════════════════════════════════════════════"
echo "TEST SUMMARY"
echo "═══════════════════════════════════════════════════════════"
echo "Total test suites: $total_tests"
echo "Failed suites: $failed_tests"

if [[ $failed_tests -eq 0 ]]; then
    echo "✓ All tests passed!"
    exit 0
else
    echo "✗ Some tests failed"
    exit 1
fi
