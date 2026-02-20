#!/usr/bin/env python3
"""
Detect the primary programming language of a repository.

Analyzes all files by extension and counts lines of code to determine
the dominant language in a project. Optimized for quick execution.
"""

import sys
import json
import argparse
import subprocess
import time
import hashlib
from pathlib import Path
from collections import defaultdict
from typing import Dict, Tuple, Optional

# Language file extension mappings, glyphs, and weights (loaded from JSON)
LANGUAGE_EXTENSIONS = {}
LANGUAGE_GLYPHS = {}
LANGUAGE_WEIGHTS = {}  # Weight multiplier for each language (default 1.0)
EXTENSION_MAP = {}  # Fast reverse lookup: extension -> language
FILENAME_MAP = {}  # Fast reverse lookup: filename -> language


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
            
            extensions = set(data.get('extensions', []))
            LANGUAGE_EXTENSIONS[lang_name] = extensions
            LANGUAGE_GLYPHS[lang_name] = data.get('glyph', '')
            LANGUAGE_WEIGHTS[lang_name] = data.get('weight', 1.0)
            
            # Build fast reverse lookup maps
            for ext in extensions:
                if ext.startswith('.'):
                    EXTENSION_MAP[ext] = lang_name
                else:
                    # Filename without extension (e.g., "Dockerfile", "Makefile")
                    FILENAME_MAP[ext] = lang_name
    
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
    'bin', 'obj', 'logs', 'tmp', 'temp',
    'release', 'releases',
    '.github', '.gitlab', '.bitbucket',
    '.conda', '.mypy_cache', '.ruff_cache', '.tox',
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


def get_cache_dir() -> Path:
    """Get the cache directory, creating it if necessary."""
    cache_dir = Path.home() / ".cache" / "detect-repo-language"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def get_cache_key(repo_path: str) -> str:
    """
    Generate a cache key for a repository.
    
    Tries to use git commit hash, falls back to repo path hash.
    """
    repo_root = Path(repo_path).resolve()
    
    # Try to get git commit hash (most reliable cache key)
    try:
        result = subprocess.run(
            ['git', '-C', str(repo_root), 'rev-parse', 'HEAD'],
            capture_output=True,
            timeout=1,
            text=True
        )
        if result.returncode == 0:
            return result.stdout.strip()[:12]  # First 12 chars of commit hash
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    # Fallback: hash the repo path
    return hashlib.md5(str(repo_root).encode()).hexdigest()[:12]


def get_cache_file(repo_path: str) -> Path:
    """Get the cache file path for a repository."""
    cache_key = get_cache_key(repo_path)
    return get_cache_dir() / f"repo_{cache_key}.json"


def read_cache(repo_path: str, cache_expiry: int) -> Optional[Dict[str, Tuple[int, int]]]:
    """
    Read cached results if available and not expired.
    
    Args:
        repo_path: Path to the repository
        cache_expiry: Cache expiration time in seconds (0 = never expire)
        
    Returns:
        Cached stats dict if valid, None otherwise
    """
    cache_file = get_cache_file(repo_path)
    
    if not cache_file.exists():
        return None
    
    try:
        with open(cache_file, 'r') as f:
            cache_data = json.load(f)
        
        # Check expiration
        if cache_expiry > 0:
            cache_time = cache_data.get("_timestamp", 0)
            if time.time() - cache_time > cache_expiry:
                return None  # Cache expired
        
        # Return cached stats
        stats = cache_data.get("stats", {})
        # Convert lists back to tuples
        return {lang: tuple(counts) for lang, counts in stats.items()}
    except (json.JSONDecodeError, IOError, KeyError):
        return None


def write_cache(repo_path: str, stats: Dict[str, Tuple[int, int]]) -> None:
    """
    Write analysis results to cache.
    
    Args:
        repo_path: Path to the repository
        stats: Language statistics to cache
    """
    cache_file = get_cache_file(repo_path)
    
    try:
        cache_data = {
            "_timestamp": time.time(),
            "_repo_path": str(Path(repo_path).resolve()),
            "stats": {lang: list(counts) for lang, counts in stats.items()}
        }
        
        with open(cache_file, 'w') as f:
            json.dump(cache_data, f, indent=2)
    except IOError:
        pass  # Silently skip cache write on permission errors


def clear_cache(repo_path: Optional[str] = None) -> None:
    """
    Clear cache for a specific repository or all repositories.
    
    Args:
        repo_path: Specific repo to clear, or None to clear all
    """
    cache_dir = get_cache_dir()
    
    if repo_path:
        # Clear cache for specific repo
        cache_file = get_cache_file(repo_path)
        if cache_file.exists():
            cache_file.unlink()
            print(f"Cleared cache for {repo_path}")
    else:
        # Clear all cache
        import shutil
        if cache_dir.exists():
            shutil.rmtree(cache_dir)
            cache_dir.mkdir(parents=True, exist_ok=True)
            print("Cleared all caches")


def is_git_repo(repo_path: str) -> bool:
    """
    Check if the given path is a git repository or inside one.
    
    Fast-path: checks .git folder first (instant for non-git dirs).
    If not found locally, tries git command (finds parent repos in nested dirs).
    """
    repo_root = Path(repo_path).resolve()
    
    # Fast check: .git directory/file in current directory (instant filesystem check)
    git_dir = repo_root / ".git"
    if git_dir.exists():
        return True
    
    # Not at repo root, but could be inside a repo - check via git command
    # This finds parent repos and handles nested directories correctly
    try:
        result = subprocess.run(
            ['git', '-C', str(repo_root), 'rev-parse', '--git-dir'],
            capture_output=True,
            timeout=2
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        # git command failed/timed out - not in a git repo
        return False


def count_lines(file_path: Path) -> int:
    """Count lines in a file quickly."""
    try:
        # Skip files larger than 10MB (likely generated or minified)
        if file_path.stat().st_size > 10 * 1024 * 1024:
            return 0
        
        # Fast line counting: read in chunks and count newlines
        # Much faster than readlines() for large files
        with open(file_path, 'rb') as f:
            count = 0
            for chunk in iter(lambda: f.read(1024*1024), b''):
                count += chunk.count(b'\n')
        return count
    except Exception:
        return 0


def get_file_language(file_path: Path) -> Optional[str]:
    """Determine the language of a file based on extension and name (optimized)."""
    # Check by filename first (e.g., Dockerfile, Makefile) - O(1) lookup
    if file_path.name in FILENAME_MAP:
        return FILENAME_MAP[file_path.name]
    
    # Check by extension - O(1) lookup
    suffix = file_path.suffix.lower()
    if suffix in EXTENSION_MAP:
        return EXTENSION_MAP[suffix]
    
    return None

def check_dir(repo_path: str) -> None:
    repo_root = Path(repo_path).resolve()
    if not repo_root.is_dir():
        print(f"Error: {repo_path} is not a directory", file=sys.stderr)
        sys.exit(1)
    
    # Check if it's a git repository
    if not is_git_repo(repo_path):
        sys.exit(0)  # Exit silently (suitable for Starship integration)


def analyze_repository(repo_path: str) -> Dict[str, Tuple[int, int]]:
    """
    Analyze a repository and count lines of code by language.
    
    Args:
        repo_path: Path to the repository root
        
    Returns:
        Dictionary mapping language -> (file_count, line_count)
    """
    repo_root = Path(repo_path).resolve()
    
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
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Disable caching for this run"
    )
    parser.add_argument(
        "--cache-expiry",
        type=int,
        default=3600,
        help="Cache expiration time in seconds (default: 3600 = 1 hour, 0 = never expire)"
    )
    parser.add_argument(
        "--clear-cache",
        nargs="?",
        const="all",
        metavar="REPO_PATH",
        help="Clear cache (all caches if no path specified, or specific repo cache)"
    )
    
    args = parser.parse_args()

    # Handle cache clearing
    if args.clear_cache is not None:
        clear_cache(args.clear_cache if args.clear_cache != "all" else None)
        sys.exit(0)

    check_dir(args.repo_path)  # Validate directory and git repo before loading config
    load_language_config()  # Load language definitions after confirming repo is valid
    
    # Try to read from cache first (if caching enabled)
    stats = None
    if not args.no_cache:
        stats = read_cache(args.repo_path, args.cache_expiry)
    
    # If cache miss, analyze repository
    if stats is None:
        stats = analyze_repository(args.repo_path)
        # Write to cache for future runs
        if not args.no_cache:
            write_cache(args.repo_path, stats)
    
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
