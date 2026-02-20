#!/usr/bin/env python3
"""
Detect the primary programming language of a repository.

Analyzes all files by extension and counts lines of code to determine
the dominant language in a project. Optimized for quick execution.
"""

import os
import sys
import json
import argparse
import subprocess
from pathlib import Path
from collections import defaultdict
from typing import Dict, Tuple, Optional

# Language file extension mappings, glyphs, and weights (loaded from JSON)
LANGUAGE_EXTENSIONS = {}
LANGUAGE_GLYPHS = {}
LANGUAGE_WEIGHTS = {}  # Weight multiplier for each language (default 1.0)


def load_language_config():
    """
    Load language configuration from the languages/ folder.
    
    Recursively loads all .json files from the languages folder.
    Each file should contain: {"extensions": [...], "glyph": "...", "weight": 1.0}
    Weight is optional (default: 1.0). Use < 1.0 to deprioritize, > 1.0 to prioritize.
    """
    global LANGUAGE_EXTENSIONS, LANGUAGE_GLYPHS, LANGUAGE_WEIGHTS
    
    # Try to find languages folder in multiple locations
    languages_dir = None
    script_dir = Path(__file__).parent
    
    # Search paths in order of preference
    search_paths = [
        script_dir / "languages",  # Development/direct execution
        script_dir.parent / "share" / "detect-repo-language" / "languages",  # System install
        Path("/usr/share/detect-repo-language/languages"),  # Arch Linux standard
        Path("/usr/local/share/detect-repo-language/languages"),  # Local system install
    ]
    
    # Also check in the wheel data directory structure
    import site
    for site_dir in site.getsitepackages():
        search_paths.insert(0, Path(site_dir) / "detect_repo_language-1.0.0.data" / "data" / "languages")
    
    for path in search_paths:
        if path.is_dir():
            languages_dir = path
            break
    
    if not languages_dir:
        print(f"Error: {search_paths[0]} folder not found", file=sys.stderr)
        print(f"Searched in: {', '.join(str(p) for p in search_paths)}", file=sys.stderr)
        sys.exit(1)
    
    # Find all .json files recursively
    json_files = sorted(languages_dir.rglob("*.json"))
    
    # Filter out template/documentation files (those starting with uppercase)
    json_files = [f for f in json_files if not f.stem[0].isupper()]
    
    if not json_files:
        print(f"Error: No language definitions found in {languages_dir}", file=sys.stderr)
        sys.exit(1)
    
    # Mapping for special language name cases
    name_mapping = {
        "c-sharp": "C#",
        "c++": "C++",
    }
    
    try:
        for config_file in json_files:
            # Get language name from filename (remove .json)
            lang_name = config_file.stem
            
            # Apply special name mappings
            if lang_name in name_mapping:
                lang_name = name_mapping[lang_name]
            else:
                # Convert to Title Case (e.g., python -> Python, javascript -> Javascript)
                lang_name = lang_name.title()
                # Handle special cases like "Json" -> "JSON", "Yaml" -> "YAML"
                lang_name = lang_name.replace("Json", "JSON").replace("Yaml", "YAML").replace("Xml", "XML").replace("Html", "HTML").replace("Php", "PHP").replace("Sql", "SQL").replace("Css", "CSS").replace("Toml", "TOML")
            
            with open(config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            LANGUAGE_EXTENSIONS[lang_name] = set(data.get('extensions', []))
            LANGUAGE_GLYPHS[lang_name] = data.get('glyph', '')
            LANGUAGE_WEIGHTS[lang_name] = data.get('weight', 1.0)
    
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading language definitions: {e}", file=sys.stderr)
        sys.exit(1)

# Directories and files to ignore
IGNORE_DIRS = {
    '.git', '.hg', '.svn',
    'node_modules', 'vendor', 'venv', '.venv', 'env', '.env',
    '.cache', '.pytest_cache', '__pycache__', '.egg-info',
    'build', 'dist', 'target', 'out', '.gradle',
    '.idea', '.vscode', '.DS_Store',
    'coverage', '.nyc_output',
}

IGNORE_FILES = {
    '.DS_Store', 'Thumbs.db', '.gitignore', '.gitattributes',
    'package-lock.json', 'yarn.lock', 'poetry.lock', 'Gemfile.lock',
}


def should_ignore(path: Path, root: Path) -> bool:
    """Check if a path should be ignored."""
    # Check if any part of the path is in ignore list
    for part in path.relative_to(root).parts:
        if part in IGNORE_DIRS:
            return True
    
    if path.name in IGNORE_FILES:
        return True
    
    return False


def is_git_repo(repo_path: str) -> bool:
    """
    Check if the given path is a git repository.
    
    Tries using `git` command first, falls back to checking .git folder.
    """
    repo_root = Path(repo_path).resolve()
    
    # Try using git command first
    try:
        result = subprocess.run(
            ['git', '-C', str(repo_root), 'rev-parse', '--git-dir'],
            capture_output=True,
            timeout=2
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        # git command timed out or not installed, fall back to .git folder check
        pass
    
    # Fallback: check for .git directory
    git_dir = repo_root / ".git"
    return git_dir.exists()


def count_lines(file_path: Path) -> int:
    """Count non-empty, non-comment lines in a file."""
    try:
        # Skip files larger than 10MB (likely generated or minified)
        if file_path.stat().st_size > 10 * 1024 * 1024:
            return 0
        
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        
        # Simple heuristic: count non-empty lines
        # Subtract comment lines for some languages
        count = 0
        for line in lines:
            stripped = line.strip()
            # Skip empty lines
            if not stripped:
                continue
            # Rough comment filtering (not perfect, but good enough)
            if stripped.startswith('#') or stripped.startswith('//') or stripped.startswith('/*'):
                continue
            count += 1
        return count
    except Exception:
        return 0


def get_file_language(file_path: Path) -> Optional[str]:
    """Determine the language of a file based on extension and name."""
    # Check by filename first (e.g., Dockerfile, Makefile)
    for lang, exts in LANGUAGE_EXTENSIONS.items():
        if file_path.name in exts:
            return lang
    
    # Check by extension
    suffix = file_path.suffix.lower()
    for lang, exts in LANGUAGE_EXTENSIONS.items():
        if suffix in exts:
            return lang
    
    return None


def analyze_repository(repo_path: str) -> Dict[str, Tuple[int, int]]:
    """
    Analyze a repository and count lines of code by language.
    
    Args:
        repo_path: Path to the repository root
        
    Returns:
        Dictionary mapping language -> (file_count, line_count)
    """
    repo_root = Path(repo_path).resolve()
    
    if not repo_root.is_dir():
        print(f"Error: {repo_path} is not a directory", file=sys.stderr)
        sys.exit(1)
    
    # Check if it's a git repository
    if not is_git_repo(repo_path):
        sys.exit(0)  # Exit silently (suitable for Starship integration)
    
    language_stats = defaultdict(lambda: [0, 0])  # [file_count, line_count]
    
    # Walk through all files
    for file_path in repo_root.rglob('*'):
        if should_ignore(file_path, repo_root):
            continue
        
        if not file_path.is_file():
            continue
        
        language = get_file_language(file_path)
        if language:
            lines = count_lines(file_path)
            # Apply language weight multiplier
            weight = LANGUAGE_WEIGHTS.get(language, 1.0)
            weighted_lines = int(lines * weight)
            language_stats[language][0] += 1
            language_stats[language][1] += weighted_lines
    
    return {lang: tuple(stats) for lang, stats in language_stats.items()}


def print_results(stats: Dict[str, Tuple[int, int]], with_glyph: bool = False) -> None:
    """Print the analysis results."""
    if not stats:
        print("No recognized source files found.")
        return
    
    # Sort by lines of code (descending)
    sorted_stats = sorted(stats.items(), key=lambda x: x[1][1], reverse=True)
    
    print("\n" + "=" * 60)
    print("Repository Language Analysis")
    print("=" * 60)
    print(f"{'Language':<20} {'Files':<10} {'Lines of Code':<15}")
    print("-" * 60)
    
    total_files = 0
    total_lines = 0
    
    for language, (file_count, line_count) in sorted_stats:
        lang_display = format_language_output(language, with_glyph)
        print(f"{lang_display:<20} {file_count:<10} {line_count:<15,}")
        total_files += file_count
        total_lines += line_count
    
    print("-" * 60)
    print(f"{'TOTAL':<20} {total_files:<10} {total_lines:<15,}")
    print("=" * 60)
    
    primary_language = sorted_stats[0][0]
    primary_lines = sorted_stats[0][1][1]
    percentage = (primary_lines / total_lines * 100) if total_lines > 0 else 0
    
    primary_display = format_language_output(primary_language, with_glyph)
    print(f"\n✓ Primary Language: {primary_display}")
    print(f"  ({primary_lines:,} lines, {percentage:.1f}% of total)")
    print()


def get_primary_language(stats: Dict[str, Tuple[int, int]]) -> Optional[str]:
    """Get the primary language from statistics."""
    if not stats:
        return None
    sorted_stats = sorted(stats.items(), key=lambda x: x[1][1], reverse=True)
    return sorted_stats[0][0]


def format_language_output(language: str, with_glyph: bool = False) -> str:
    """Format language name with optional glyph."""
    if not with_glyph:
        return language
    glyph = LANGUAGE_GLYPHS.get(language, '')
    if glyph:
        return f"{glyph} {language}"
    return language


def main():
    """Main entry point."""
    # Load language configuration from JSON
    load_language_config()
    
    parser = argparse.ArgumentParser(
        description="Detect the primary programming language of a repository",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  detect_repo_language.py .                                    # Full analysis
  detect_repo_language.py --primary-only .                     # Starship integration
  detect_repo_language.py --primary-only --with-glyph .        # With icon
  detect_repo_language.py --primary-only --prefix "Lang: " .   # With prefix
  detect_repo_language.py --json .                             # JSON output
        """
    )
    parser.add_argument(
        "repo_path",
        nargs="?",
        default=".",
        help="Path to repository (default: current directory)"
    )
    parser.add_argument(
        "--primary-only",
        action="store_true",
        help="Output only the primary language name (lightweight mode for starship)"
    )
    parser.add_argument(
        "--with-glyph",
        action="store_true",
        help="Include Nerdfont glyph/icon in output"
    )
    parser.add_argument(
        "--prefix",
        default="",
        help="Add a prefix to the output (e.g., 'Language: ' or '󱔎 '). Works with --primary-only"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results in JSON format"
    )
    
    args = parser.parse_args()
    
    stats = analyze_repository(args.repo_path)
    
    if args.primary_only:
        language = get_primary_language(stats)
        if language:
            output = format_language_output(language, args.with_glyph)
            if args.prefix:
                output = f"{args.prefix}{output}"
            print(output)
    elif args.json:
        output = {
            "primary_language": get_primary_language(stats),
            "primary_glyph": LANGUAGE_GLYPHS.get(get_primary_language(stats), "") if get_primary_language(stats) else None,
            "stats": {lang: {"files": count, "lines": lines} 
                     for lang, (count, lines) in stats.items()}
        }
        print(json.dumps(output, indent=2))
    else:
        print_results(stats, args.with_glyph)


if __name__ == "__main__":
    main()
