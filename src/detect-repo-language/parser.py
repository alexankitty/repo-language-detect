import argparse

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Detect the primary programming language of a repository",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
  {__package__} --primary-only .                     # Starship integration
  {__package__} --primary-only --with-glyph .        # With icon
  {__package__} --primary-only --prefix "Lang: " .   # With prefix
  {__package__} --json .                             # JSON output
        """
    )
    parser.add_argument(
        "repo_path",
        nargs="?",
        default=".",
        help="Path to repository (default: current directory)"
    )
    parser.add_argument(
        '-p',
        "--primary-only",
        action="store_true",
        help="Output only the primary language name (lightweight mode for starship)"
    )
    parser.add_argument(
        '-g',
        "--with-glyph",
        action="store_true",
        help="Include Nerdfont glyph/icon in output"
    )
    parser.add_argument(
        "-P",
        "--prefix",
        default="",
        help="Add a prefix to the output (e.g., 'Language: ' or '󱔎 '). Works with --primary-only"
    )
    parser.add_argument(
        '-j',
        "--json",
        action="store_true",
        help="Output results in JSON format"
    )
    parser.add_argument(
        '-n',
        "--no-cache",
        action="store_true",
        help="Disable caching for this run"
    )
    parser.add_argument(
        '-e',
        "--cache-expiry",
        type=int,
        default=3600,
        help="Cache expiration time in seconds (default: 3600 = 1 hour, 0 = never expire)"
    )
    parser.add_argument(
        '-w',
        "--weighted",
        action="store_true",
        help="Show weighted line counts instead of raw line counts"
    )
    parser.add_argument(
        '-a',
        "--all",
        action="store_true",
        help="Show both raw and weighted line counts"
    )
    parser.add_argument(
        '-C',
        "--clear-cache",
        nargs="?",
        const="all",
        metavar="REPO_PATH",
        help="Clear cache (all caches if no path specified, or specific repo cache)"
    )
    return parser.parse_args()