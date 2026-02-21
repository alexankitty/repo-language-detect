# Release Notes - v1.3.0

## Overview

Repository Language Detector v1.3.0 brings improved package structure support and enhanced testing infrastructure.

## What's New

- **Restructured package layout** - Module moved to `src/` for better development practices
- **Improved build system** - Updated setup.py and pyproject.toml for proper package discovery and data file inclusion
- **Comprehensive test suite** - Added wheel build validation and PKGBUILD verification tests
- **Dynamic test coverage** - Tests now automatically adapt to actual repository structure
- **Enhanced diagnostics** - Tests provide better debugging information on failures

## Improvements

- Package now correctly includes language definition files in wheels
- Better support for different installation methods (pip, wheel, PKGBUILD)

## Installation

```bash
pip install .
```

Or with wheel:
```bash
python3 -m build --wheel
pip install dist/*.whl
```

## Testing

Run complete test suite:
```bash
bash tests/test_all.sh
```

## Requirements

- Python 3.7+
- No external dependencies

## Platform Support

- Linux, (macOS, Windows untested)
- Arch Linux (PKGBUILD support)
- PyPI installation
