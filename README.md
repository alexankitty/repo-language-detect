# Repository Language Detector

A Python script that analyzes a repository to determine its primary programming language by counting files and lines of code.  
Yes this was entirely vibe coded. No I don't really care. No this statement did not come from the AI. Use it if you want, it works, I just didn't want to make the effort.

## Features

- 🔍 **Git-only**: Only analyzes git repositories (exits silently otherwise)
- 📁 Scans all files in a repository recursively
- 🗣️ Supports 30+ programming languages and formats
- 📊 Counts both files and lines of code (excluding comments/blanks)
- 🚫 Ignores common non-source directories (`node_modules`, `.git`, `venv`, etc.)
- 📈 Provides formatted output with statistics
- 🎯 Identifies the primary language with percentage breakdown
- 🎨 Optional Nerdfont glyph/icon display
- ⚡ Lightweight (~66ms) - ideal for shell prompt integration

## Installation

No external dependencies required! Just ensure you have Python 3.7+.

```bash
chmod +x detect_repo_language.py
```

## Project Structure

```
lang-detect/
├── detect_repo_language.py    # Main script
├── languages/                 # Language definitions (auto-loaded)
│   ├── python.json
│   ├── javascript.json
│   ├── c-sharp.json
│   ├── c++.json
│   └── ... (one file per language)
├── README.md
└── .git/
```

All language configurations are discovered and loaded recursively from the `languages/` folder.

## Usage

**Requirements:**
- The target directory must be a git repository (must contain a `.git` folder)
- If run on a non-git directory, the script exits silently with code 0

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

**With custom prefix:**
```bash
./detect_repo_language.py --primary-only --prefix "Language: "
./detect_repo_language.py --primary-only --prefix "󱔎 "
```
Output: Prefixed language (e.g., `Language: Python` or `󱔎 Python`)

**Combining options:**
```bash
./detect_repo_language.py --primary-only --with-glyph --prefix "📝 "
```
Output: `📝  Python`

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

1. **Loads language definitions** from the `languages/` folder (recursively)
2. **Traverses** all files in the repository
3. **Filters out** common non-source directories and files
4. **Identifies** each file's language by extension
5. **Counts** lines of code (excluding empty lines and comments)
6. **Displays** results sorted by lines of code

## Configuration

Language definitions (file extensions and Nerdfont glyphs) are organized in the `languages/` folder. Each language has its own JSON file, making it very easy to:
- Add support for new languages by creating a new file
- Customize glyph icons for your setup
- Update extensions without touching the code
- Organize languages hierarchically (subfolders are supported)

### Adding a New Language

The easiest way to add a new language:

1. **Copy the template file:**
   ```bash
   cp languages/TEMPLATE.json languages/mylanguage.json
   ```

2. **Edit the file** with your language's extensions and Nerdfont glyph:
   ```json
   {
     "extensions": [".ext1", ".ext2"],
     "glyph": "\uXXXX"
   }
   ```

3. **Save and test** - the script will automatically discover your new language!

For detailed instructions, examples, and tips for finding Nerdfont glyphs, see [languages/README.md](languages/README.md).

For example, to add Lua support, create `languages/lua.json`:

```json
{
  "extensions": [".lua"],
  "glyph": "\ue60a"
}
```

The script will automatically:
- Discover the new file on next run
- Convert the filename to the language name (e.g., `lua.json` → `Lua`)
- Add it to the analysis

### Language Name Mapping

The script automatically converts filenames to proper language names:
- `python.json` → `Python`
- `c-sharp.json` → `C#`
- `c++.json` → `C++`
- `json.json` → `JSON`
- `yaml.json` → `YAML`
- `xml.json` → `XML`
- `html.json` → `HTML`

For special cases, edit the `name_mapping` dictionary in the script.

## Notes

- **Git Detection:** Uses `git rev-parse` command first if git is installed. Falls back to checking for `.git` folder if git is unavailable. This ensures robust detection across different environments.
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

**With custom prefix:**
```toml
[custom.language]
command = "detect_repo_language.py --primary-only --prefix '󱔎 '"
when = true
style = "bold magenta"
```

**With prefix and glyph:**
```toml
[custom.language]
command = "detect_repo_language.py --primary-only --with-glyph --prefix '📝 '"
when = true
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

## Testing

A comprehensive test suite is available in the `tests/` folder to verify functionality:

```bash
# Run all tests
bash tests/test_all.sh

# Run specific test suites
bash tests/test_basic.sh          # Core functionality
bash tests/test_prefix.sh         # Prefix option
bash tests/test_languages.sh      # Language loading
bash tests/test_git_detection.sh  # Git detection
```

See [tests/README.md](tests/README.md) for detailed information about the test suite.

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
