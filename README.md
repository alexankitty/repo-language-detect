# Repository Language Detector

A Python script that analyzes a repository to determine its primary programming language by counting files and lines of code.  
Yes this was entirely vibe coded. No I don't really care. No this statement did not come from the AI. Use it if you want, it works, I just didn't want to make the effort.

## Features

- Scans all files in a repository recursively
- Supports 30+ programming languages and formats
- Counts both files and lines of code (excluding comments/blanks)
- Ignores common non-source directories (`node_modules`, `.git`, `venv`, etc.)
- Provides formatted output with statistics
- Identifies the primary language with percentage breakdown

## Installation

No external dependencies required! Just ensure you have Python 3.7+.

```bash
chmod +x detect_repo_language.py
```

## Usage

**Full analysis (default):**
```bash
./detect_repo_language.py
./detect_repo_language.py /path/to/repo
```

**Lightweight mode (for Starship integration):**
```bash
./detect_repo_language.py --primary-only
./detect_repo_language.py --primary-only /path/to/repo
```
Output: Just the language name (e.g., `Python`)

**With Nerdfont icon/glyph:**
```bash
./detect_repo_language.py --primary-only --with-glyph
./detect_repo_language.py --with-glyph
```
Output: Language with icon (e.g., ` Python`)

**JSON output:**
```bash
./detect_repo_language.py --json
./detect_repo_language.py --json /path/to/repo
```

**Example output (default mode):**
```
============================================================
Repository Language Analysis
============================================================
Language             Files      Lines of Code  
------------------------------------------------------------
 Python              45         12,342         
 JavaScript          23         8,901          
 YAML                8          234            
 JSON                15         156            
 Markdown            12         892            
------------------------------------------------------------
TOTAL                103        22,525         
============================================================

✓ Primary Language: Python
  (12,342 lines, 54.8% of total)
```

## Supported Languages

- **Core:** Python, JavaScript, TypeScript, Java, C, C++, C#
- **Web:** HTML, CSS, PHP
- **Systems:** Rust, Go, Ruby, Swift, Kotlin
- **Data/Science:** R, Julia, Scala, SQL
- **Scripting:** Perl, Shell, Elixir, Erlang, Haskell
- **Config/Markup:** YAML, JSON, TOML, XML, Markdown, Dockerfile, Makefile

## How It Works

1. **Traverses** all files in the repository
2. **Filters out** common non-source directories and files
3. **Identifies** each file's language by extension
4. **Counts** lines of code (excluding empty lines and comments)
5. **Displays** results sorted by lines of code

## Notes

- Comment detection is basic (lines starting with `#`, `//`, `/*`)
- For accurate results, ensure the repository doesn't have generated code in version control
- Ignores package lock files, build artifacts, and cache directories automatically
- **Performance:** Optimized for speed (~66ms on typical projects) - suitable for shell prompts

## Starship Integration

Add language detection to your Starship prompt with optional icons:

**Basic version (language name only):**
```toml
[custom.language]
command = "detect_repo_language.py --primary-only"
when = true
```

**With Nerdfont icon (recommended for Nerd Font users):**
```toml
[custom.language]
command = "detect_repo_language.py --primary-only --with-glyph"
when = true
style = "bold blue"
```

**Full example in `starship.toml`:**
```toml
[custom.language]
command = "detect_repo_language.py --primary-only --with-glyph"
symbol = "󱔎 "
when = true
style = "bold cyan"
```

This will display the repository's primary language (with icon if enabled) in your shell prompt as you navigate between projects. The `--primary-only` flag ensures minimal overhead (~66ms) suitable for real-time prompt updates.

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
