from . import LANGUAGE_GLYPHS, language, formatter, parser, cache, analyze
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
    language = analyze.get_primary_language(stats)
    if language:
        output = formatter.format_language_output(language, args.with_glyph)
        if args.prefix:
            output = f"{args.prefix}{output}"
        print(output)
elif args.json:
    weighted_stats = analyze.apply_weights_to_stats(stats)
    output_all: dict[str, object] = {
        "primary_language": analyze.get_primary_language(stats),
        "primary_glyph": LANGUAGE_GLYPHS.get(analyze.get_primary_language(stats), "") if analyze.get_primary_language(stats) else None,
        "stats": {lang: {"files": count, "lines": lines} 
                    for lang, (count, lines) in weighted_stats.items()}
    }
    print(json.dumps(output_all, indent=2))
else:
    show_mode = 'both' if args.all else ('weighted' if args.weighted else 'raw')
    formatter.print_results(stats, args.with_glyph, show_mode)