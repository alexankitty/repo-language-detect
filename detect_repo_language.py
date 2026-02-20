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
from pathlib import Path
from collections import defaultdict
from typing import Dict, Tuple, Optional

# Language file extension mappings
LANGUAGE_EXTENSIONS = {
    'Python': {'.py', '.pyw', '.pyx', '.pyi', '.pyc'},
    'JavaScript': {'.js', '.jsx', '.mjs', '.cjs'},
    'TypeScript': {'.ts', '.tsx'},
    'Java': {'.java'},
    'C': {'.c', '.h'},
    'C++': {'.cpp', '.cc', '.cxx', '.c++', '.hpp', '.hh', '.h++'},
    'C#': {'.cs'},
    'Ruby': {'.rb', '.rbw'},
    'Go': {'.go'},
    'Rust': {'.rs'},
    'PHP': {'.php', '.php3', '.php4', '.php5', '.phtml'},
    'Swift': {'.swift'},
    'Kotlin': {'.kt', '.kts'},
    'Scala': {'.scala'},
    'Haskell': {'.hs', '.lhs'},
    'R': {'.r', '.R', '.Rd'},
    'Julia': {'.jl'},
    'Elixir': {'.ex', '.exs'},
    'Erlang': {'.erl', '.hrl'},
    'Perl': {'.pl', '.pm', '.pod'},
    'Shell': {'.sh', '.bash', '.zsh', '.fish'},
    'SQL': {'.sql'},
    'HTML': {'.html', '.htm', '.xhtml'},
    'CSS': {'.css', '.scss', '.sass', '.less'},
    'YAML': {'.yaml', '.yml'},
    'JSON': {'.json'},
    'XML': {'.xml', '.xsd', '.xsl'},
    'Markdown': {'.md', '.markdown', '.mdown', '.mkd', '.mkdn'},
    'TOML': {'.toml'},
    'Dockerfile': {'Dockerfile'},
    'Makefile': {'Makefile', 'makefile'},
}

# Nerdfont glyphs for languages
LANGUAGE_GLYPHS = {
    'Python': '\ue73c',  # 
    'JavaScript': '\ue74e',  # 
    'TypeScript': '\ue628',  # 
    'Java': '\ue738',  # 
    'C': '\ue61e',  # 
    'C++': '\ue61d',  # 
    'C#': '\ue905',  # 
    'Ruby': '\ue739',  # 
    'Go': '\ueab0',  # 
    'Rust': '\ue7a8',  # 
    'PHP': '\ue73d',  # 
    'Swift': '\ufbe3',  # 
    'Kotlin': '\ue636',  # 
    'Scala': '\ue737',  # 
    'Haskell': '\ue777',  # 
    'R': '\uf4f0',  # 
    'Julia': '\ue624',  # 
    'Elixir': '\ue62b',  # 
    'Erlang': '\ue7b1',  # 
    'Perl': '\ue769',  # 
    'Shell': '\uf489',  # 
    'SQL': '\ue706',  # 
    'HTML': '\ue736',  # 
    'CSS': '\ue749',  # 
    'YAML': '\ue6a0',  # 
    'JSON': '\ue60b',  # 
    'XML': '\ue619',  # 
    'Markdown': '\ue729',  # 
    'TOML': '\ue60b',  # 
    'Dockerfile': '\uf308',  # 
    'Makefile': '\ue628',  # 
}

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
            language_stats[language][0] += 1
            language_stats[language][1] += lines
    
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
    parser = argparse.ArgumentParser(
        description="Detect the primary programming language of a repository",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  detect_repo_language.py .                         # Full analysis
  detect_repo_language.py --primary-only .          # Starship integration
  detect_repo_language.py --primary-only --with-glyph .  # With icon
  detect_repo_language.py --json .                  # JSON output
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
