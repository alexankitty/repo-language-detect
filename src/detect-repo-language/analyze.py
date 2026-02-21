import sys
from pathlib import Path
from typing import Dict, Tuple, Optional
import subprocess
from . import LANGUAGE_WEIGHTS, FILENAME_MAP, EXTENSION_MAP, IGNORE_DIRS, IGNORE_FILES
from collections import defaultdict

def should_ignore(path: Path, root: Path) -> bool:
    """Check if a path should be ignored."""
    for part in path.relative_to(root).parts:
        if part in IGNORE_DIRS:
            return True
    
    if path.name in IGNORE_FILES:
        return True
    
    return False

def is_git_repo(repo_path: str) -> bool:
    """
    Check if the given path is a git repository or inside one.
    
    Fast-path: checks .git folder first (instant for non-git dirs).
    If not found locally, tries git command (finds parent repos in nested dirs).
    """
    repo_root = Path(repo_path).resolve()
    
    git_dir = repo_root / ".git"
    if git_dir.exists():
        return True
    
    try:
        result = subprocess.run(
            ['git', '-C', str(repo_root), 'rev-parse', '--git-dir'],
            capture_output=True,
            timeout=2
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
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
    if file_path.name in FILENAME_MAP:
        return FILENAME_MAP[file_path.name]
    
    suffix = file_path.suffix.lower()
    if suffix in EXTENSION_MAP:
        return EXTENSION_MAP[suffix]
    
    return None

def check_dir(repo_path: str) -> None:
    repo_root = Path(repo_path).resolve()
    if not repo_root.is_dir():
        print(f"Error: {repo_path} is not a directory", file=sys.stderr)
        sys.exit(1)
    
    if not is_git_repo(repo_path):
        sys.exit(0)  # Exit silently (suitable for Starship integration)


def analyze_repository(repo_path: str) -> Dict[str, Tuple[int, ...]]:
    """
    Analyze a repository and count lines of code by language.
    
    Args:
        repo_path: Path to the repository root
        
    Returns:
        Dictionary mapping language -> (file_count, line_count)
        Note: Returns UNWEIGHTED line counts. Weights are applied at display time.
    """
    repo_root = Path(repo_path).resolve()
    
    language_stats: dict[str, list[int]] = defaultdict(lambda: [0, 0])  # [file_count, line_count]
    
    for file_path in repo_root.rglob('*'):
        if should_ignore(file_path, repo_root):
            continue
        
        if not file_path.is_file():
            continue
        
        language = get_file_language(file_path)
        if language:
            lines = count_lines(file_path)
            # Store UNWEIGHTED line counts (weights applied at display time)
            language_stats[language][0] += 1
            language_stats[language][1] += lines
    
    return {lang: tuple(stats) for lang, stats in language_stats.items()}

def get_primary_language(stats: Dict[str, Tuple[int, ...]]) -> str:
    """Get the primary language from statistics."""
    if not stats:
        return 'None'
    # Apply weights before determining primary language
    stats = apply_weights_to_stats(stats)
    sorted_stats = sorted(stats.items(), key=lambda x: x[1][1], reverse=True)
    return sorted_stats[0][0]


def apply_weights_to_stats(stats: Dict[str, Tuple[int, ...]]) -> Dict[str, Tuple[int, ...]]:
    """
    Apply language weights to raw line counts.
    
    Args:
        stats: Dictionary with (file_count, unweighted_line_count) tuples
        
    Returns:
        Same structure with weighted line counts
    """
    weighted_stats: dict[str, Tuple[int, int]] = {}
    for lang, (file_count, line_count) in stats.items():
        weight = LANGUAGE_WEIGHTS.get(lang, 1.0)
        weighted_lines = int(line_count * weight)
        weighted_stats[lang] = (file_count, weighted_lines)
    return weighted_stats