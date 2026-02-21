# Language file extension mappings, glyphs, and weights (loaded from JSON)
VERSION = "1.3.0"
LANGUAGE_EXTENSIONS: dict[str, list[str]] = {}
LANGUAGE_GLYPHS: dict[str,str] = {}
LANGUAGE_WEIGHTS: dict[str,float] = {}  # Weight multiplier for each language (default 1.0)
EXTENSION_MAP: dict[str,str] = {}  # Fast reverse lookup: extension -> language
FILENAME_MAP: dict[str,str] = {}  # Fast reverse lookup: filename -> language

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
    'debug', 'debug-info', 'debug-symbols',
    'bower_components', 'jspm_packages',
}

IGNORE_FILES = {
    '.DS_Store', 'Thumbs.db', '.gitignore', '.gitattributes',
    'package-lock.json', 'yarn.lock', 'poetry.lock', 'Gemfile.lock',
}