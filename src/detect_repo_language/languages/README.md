# Language Definitions

Language configurations for file extension recognition.

## Adding a Language

1. Copy template: `cp TEMPLATE.json mylanguage.json`
2. Edit with your language's extensions and Nerdfont glyph:
   ```json
   {
     "extensions": [".py", ".pyw"],
     "glyph": "\ue73c",
     "weight": 1.0
   }
   ```
3. Fields:
   - `extensions`: Array of file extensions (with dot)
   - `glyph`: Nerdfont Unicode (optional, empty string `""` if none)
   - `weight`: Multiplier (optional, default 1.0; use <1.0 to deprioritize, >1.0 to prioritize)
4. Save—auto-discovered on next run!

## Naming

Filename → Language name:
- `python.json` → `Python`
- `javascript.json` → `Javascript`
- `c-sharp.json` → `C#`
- `c++.json` → `C++`
- `json.json` → `JSON`
- `yaml.json` → `YAML`

Special cases in `name_mapping` dict in main module.

## Finding Nerdfont Glyphs

1. Visit [Nerd Fonts Cheat Sheet](https://www.nerdfonts.com/cheat-sheet)
2. Search, copy Unicode (e.g., `e73c`)
3. Add backslash: `\ue73c`

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

## Language Weighting

By default, all languages have a weight of `1.0`, meaning line counts contribute equally to determining the primary language.

Use weights to adjust language detection priority:

**Examples:**

```json
{
  "extensions": [".md"],
  "glyph": "\ue729",
  "weight": 0.5
}
```
This Markdown file contributes only 50% of its line count, preventing large README files from incorrectly identifying the language as "Markdown".

```json
{
  "extensions": [".rs"],
  "glyph": "\ue7a3",
  "weight": 1.5
}
```
This Rust file contributes 150% of its line count, prioritizing Rust as the primary language.

**Common Use Cases:**
- `weight: 0.5` - Configuration/documentation files (Markdown, YAML, Makefile)
- `weight: 1.0` - Standard source code (default)
- `weight: 1.5+` - Languages you want to prioritize

## Notes

- Language definition files starting with uppercase (like `TEMPLATE.json`) are skipped by the loader
- Extensions are case-sensitive (typically use lowercase: `.py`, `.js`, etc.)
- Each language file should be small (~50-100 bytes)
- No need to restart anything - changes are picked up immediately on next run
