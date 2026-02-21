# Repository Language Detector

Analyzes a git repository to determine its primary programming language by counting files and lines of code.

## Features

- Git-only (exits silently on non-git directories)
- 31+ language support
- Smart git-aware caching
- Optional Nerdfont glyphs
- File & LOC statistics

## Installation

```bash
# Method 1: Direct (simple)
chmod +x detect_repo_language.py
python3 -m detect_repo_language --primary-only /path/to/repo

# Method 2: As Python module
pip install .

# Method 3: Arch Linux
makepkg -si  # or: cp PKGBUILD.pypi PKGBUILD && makepkg -si (for PyPI)
```

## Usage

```bash
# Primary language only
python3 -m detect_repo_language --primary-only

# With Nerdfont glyph
python3 -m detect_repo_language --primary-only --with-glyph

# With custom prefix
python3 -m detect_repo_language --primary-only --prefix "󱔎 "

# JSON output
python3 -m detect_repo_language --json

# Cache options
python3 -m detect_repo_language --no-cache              # Skip cache
python3 -m detect_repo_language --cache-expiry 0       # Never expire
python3 -m detect_repo_language --clear-cache          # Clear all
python3 -m detect_repo_language --clear-cache /path    # Clear specific
```

## Project Structure

```
src/detect-repo-language/
├── __init__.py, __main__.py, analyze.py, parser.py, cache.py, formatter.py, language.py
└── languages/                           # Language definitions (auto-discovered)
    ├── python.json, javascript.json, ...
    └── TEMPLATE.json
tests/
├── test_*.sh                           # Test suites
```

## Architecture

- Auto-discovers language configs from `languages/` folder
- Git commit hash used for cache key (invalidates on code changes)
- Ignores: `.git`, `node_modules`, `venv`, `__pycache__`, `.cache`, and 20+ other common dirs

See [PKGBUILD-README.md](PKGBUILD-README.md) for Arch Linux setup details.

- **Core:** Python, JavaScript, TypeScript, Java, C, C++, C#
- **Web:** HTML, CSS, PHP
- **Systems:** Rust, Go, Ruby, Swift, Kotlin
- **Data/Science:** R, Julia, Scala, SQL
- **Scripting:** Perl, Shell, Elixir, Erlang, Haskell
- **Config/Markup:** YAML, JSON, TOML, XML, Markdown, Dockerfile, Makefile

## How It Works

1. **Git detection** - Fast path: checks `.git` folder first, supports nested directories
2. **Cache check** - Returns instantly if cached and not expired
3. **Loads language definitions** from `languages/` folder (searches 5 locations: dev, system, Arch standard, local, wheel)
4. **Traverses** all files in the repository using fast rglob()
5. **Filters out** common non-source directories and files
6. **Identifies** each file's language using O(1) reverse lookup maps (pre-computed extension/filename → language)
7. **Counts** lines using chunked binary reading (fast newline counting)
8. **Applies weights** to specific languages (e.g., Markdown: 0.25x)
9. **Caches** results with git-aware invalidation
10. **Displays** results sorted by lines of code

## Configuration

See [languages/README.md](src/detect-repo-language/languages/README.md) for adding languages, customizing glyphs, and language name mappings.

## Notes

- **Git Detection:** Fast path checks `.git` folder first. Works in nested directories. Falls back to git command if needed.
- **Performance:** Optimized with O(1) language lookups via pre-computed maps, fast git detection, and smart caching.
- **Cache:** Automatically invalidates when git commit hash changes. Configure with `--cache-expiry` and `--clear-cache`.
- **Development:** Multiple language search paths support development, system installs, Arch Linux, wheels, and direct script execution.
- Comment detection is basic (lines starting with `#`, `//`, `/*`)
- For accurate results, ensure the repository doesn't have generated code in version control
- Ignores package lock files, build artifacts, and cache directories automatically

## Starship Integration

Add language detection to your Starship prompt with optional icons:

**Basic version (language name only):**
```toml
[custom.language]
command = "detect_repo_language.py --primary-only"
when = true
format = ' $output '
require_repo = true
```

**With Nerdfont icon (recommended for Nerd Font users):**
```toml
[custom.language]
command = "detect_repo_language.py --primary-only --with-glyph"
when = true
style = "bold blue"
format = '[ $output ]($style)'
require_repo = true
```

**With custom prefix:**
```toml
[custom.language]
command = "detect_repo_language.py --primary-only --prefix '󱔎 '"
when = true
style = "bold magenta"
require_repo = true
```

**With prefix and glyph:**
```toml
[custom.language]
command = "detect_repo_language.py --primary-only --with-glyph --prefix '📝 '"
when = true
require_repo = true
```

**Full example in `starship.toml`:**
```toml
[custom.language]
command = "detect_repo_language.py --primary-only --with-glyph"
symbol = "󱔎 "
when = true
style = "bold cyan"
format = '[$symbol $output ]($style)'
require_repo = true
```

This will display the repository's primary language (with icon if enabled) in your shell prompt as you navigate between projects.

## Testing

See [tests/README.md](tests/README.md) for test suite information.

## Examples

Check the primary language of your current project:
```bash
cd ~/my-project && ~/detect_repo_language.py
```

Get just the language name for scripting:
```bash
~/detect_repo_language.py --primary-only ~/projects/my-app
# Output: Python
```

**Get the language with Nerdfont icon:**
```bash
~/detect_repo_language.py --primary-only --with-glyph ~/projects/my-app
# Output:  Python
```

**Get JSON output for integration with other tools:**
```bash
~/detect_repo_language.py --json ~/projects/my-app
# Output includes primary_language, primary_glyph, and detailed stats
```

Use in scripting:
```bash
PRIMARY=$(~/detect_repo_language.py . | grep "Primary Language" | awk '{print $3}')
echo "This repo is primarily written in: $PRIMARY"
```
