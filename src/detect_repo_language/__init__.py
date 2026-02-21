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


def main():
    """Main entry point for the detect-repo-language command."""
    from . import language, formatter, parser, cache, analyze
    import json
    import sys

    args = parser.parse_arguments()

    if args.clear_cache is not None:
        cache.clear(args.clear_cache if args.clear_cache != "all" else None)
        sys.exit(0)

    analyze.check_dir(args.repo_path)  # Validate directory and git repo before loading config
    language.load_language_config()  # Load language definitions after confirming repo is valid

    stats = None
    if not args.no_cache:
        stats = cache.read(args.repo_path, args.cache_expiry)

    # Cache Miss
    if stats is None:
        stats = analyze.analyze_repository(args.repo_path)
        if not args.no_cache:
            cache.write(args.repo_path, stats)

    if args.primary_only:
        language_name = analyze.get_primary_language(stats)
        if language_name:
            output = formatter.format_language_output(language_name, args.with_glyph)
            if args.prefix:
                output = f"{args.prefix}{output}"
            print(output)
    elif args.json:
        weighted_stats = analyze.apply_weights_to_stats(stats)
        primary_lang = analyze.get_primary_language(stats)
        output_all: dict[str, object] = {
            "primary_language": primary_lang,
            "primary_glyph": LANGUAGE_GLYPHS.get(primary_lang, "") if primary_lang else None,
            "stats": {lang: {"files": count, "lines": lines} 
                        for lang, (count, lines) in weighted_stats.items()}
        }
        print(json.dumps(output_all, indent=2))
    else:
        show_mode = 'both' if args.all else ('weighted' if args.weighted else 'raw')
        formatter.print_results(stats, args.with_glyph, show_mode)