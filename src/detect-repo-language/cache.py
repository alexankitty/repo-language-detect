from typing import Dict, Tuple, Optional
from pathlib import Path
import subprocess
import time
import json
import hashlib


def get_dir() -> Path:
    """Get the cache directory, creating it if necessary."""
    cache_dir = Path.home() / ".cache" / "detect-repo-language"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def get_key(repo_path: str) -> str:
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


def get_file(repo_path: str) -> Path:
    """Get the cache file path for a repository."""
    cache_key = get_key(repo_path)
    return get_dir() / f"repo_{cache_key}.json"


def read(repo_path: str, cache_expiry: int) -> Optional[Dict[str, Tuple[int, ...]]]:
    """
    Read cached results if available and not expired.
    
    Args:
        repo_path: Path to the repository
        cache_expiry: Cache expiration time in seconds (0 = never expire)
        
    Returns:
        Cached stats dict if valid, None otherwise
    """
    cache_file = get_file(repo_path)
    
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


def write(repo_path: str, stats: Dict[str, Tuple[int, ...]]) -> None:
    """
    Write analysis results to cache.
    
    Args:
        repo_path: Path to the repository
        stats: Language statistics to cache
    """
    cache_file = get_file(repo_path)
    
    try:
        cache_data: dict[str, object] = {
            "_timestamp": time.time(),
            "_repo_path": str(Path(repo_path).resolve()),
            "stats": {lang: list(counts) for lang, counts in stats.items()}
        }
        
        with open(cache_file, 'w') as f:
            json.dump(cache_data, f, indent=2)
    except IOError:
        pass  # Silently skip cache write on permission errors


def clear(repo_path: Optional[str] = None) -> None:
    """
    Clear cache for a specific repository or all repositories.
    
    Args:
        repo_path: Specific repo to clear, or None to clear all
    """
    cache_dir = get_dir()
    
    if repo_path:
        # Clear cache for specific repo
        cache_file = get_file(repo_path)
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