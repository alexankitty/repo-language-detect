# Test Suite

Automated tests for `detect_repo_language`.

## Running Tests

```bash
bash test_all.sh              # Run all tests
bash test_basic.sh            # Core functionality
bash test_prefix.sh           # --prefix option
bash test_git_detection.sh    # Git detection
bash test_languages.sh        # Language loading
bash test_cache.sh            # Caching
bash test_wheel_build.sh      # Wheel build & installation
bash test_pkgbuild.sh         # PKGBUILD validation
```

## Test Coverage

- **Basic**: Primary-only, glyph, JSON, full analysis
- **Prefix**: Text/emoji/icon prefixes, combinations
- **Git**: Repo detection, non-git handling, silent exit
- **Languages**: Config loading count, template exclusion
- **Cache**: Creation, hits, expiry, clear, multi-repo
- **Wheel**: Build, contents verification, installation
- **PKGBUILD**: Syntax, variables, metadata consistency, actual build test
- **Wheel**: Build, contents verification, installation
