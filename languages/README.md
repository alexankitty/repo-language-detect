# Language Definitions

This folder contains language definitions used by `detect_repo_language.py` to identify programming languages by file extension.

## Adding a New Language

To add support for a new language, follow these steps:

1. **Copy the template:**
   ```bash
   cp TEMPLATE.json mylanguage.json
   ```

2. **Edit the file** with your language's extensions and Nerdfont glyph:
   ```json
   {
     "extensions": [".py", ".pyw"],
     "glyph": "\ue73c"
   }
   ```

3. **Fields:**
   - `extensions`: Array of file extensions (including the dot, e.g., `".py"`)
   - `glyph`: Unicode escape sequence for a Nerdfont icon (optional, can be empty string `""`)

4. **Save and test:**
   The script will automatically discover and load your new language on the next run!

## Language Name Mapping

The filename is automatically converted to a language name:

- `python.json` → `Python`
- `javascript.json` → `Javascript`
- `c-sharp.json` → `C#` (special mapping)
- `c++.json` → `C++` (special mapping)
- `json.json` → `JSON` (auto-uppercase)
- `yaml.json` → `YAML` (auto-uppercase)

For special cases that don't follow standard rules, edit the `name_mapping` dictionary in `detect_repo_language.py`.

## Finding Nerdfont Glyphs

1. Visit [Nerd Fonts Cheat Sheet](https://www.nerdfonts.com/cheat-sheet)
2. Search for your language/icon
3. Copy the Unicode codepoint (e.g., `e73c` for Python)
4. Add backslash prefix: `\ue73c`

## Examples

### Lua
```json
{
  "extensions": [".lua"],
  "glyph": "\ue60a"
}
```

### Go
```json
{
  "extensions": [".go"],
  "glyph": "\ueab0"
}
```

### Clojure
```json
{
  "extensions": [".clj", ".cljs", ".cljc"],
  "glyph": ""
}
```

## File Organization

Files can be organized hierarchically in subfolders:
- `languages/python.json`
- `languages/web/javascript.json`
- `languages/web/typescript.json`
- `languages/systems/rust.json`

The script will recursively discover all `.json` files regardless of folder depth.

## Notes

- Language definition files starting with uppercase (like `TEMPLATE.json`) are skipped by the loader
- Extensions are case-sensitive (typically use lowercase: `.py`, `.js`, etc.)
- Each language file should be small (~50-100 bytes)
- No need to restart anything - changes are picked up immediately on next run
