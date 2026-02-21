import sys
from pathlib import Path
import json
from . import LANGUAGE_EXTENSIONS, LANGUAGE_GLYPHS, LANGUAGE_WEIGHTS, EXTENSION_MAP, FILENAME_MAP, VERSION


def load_language_config():
    """
    Load language configuration from the languages/ folder.
    
    Recursively loads all .json files from the languages folder.
    Each file should contain: {"extensions": [...], "glyph": "...", "weight": 1.0}
    Weight is optional (default: 1.0). Use < 1.0 to deprioritize, > 1.0 to prioritize.
    """
    
    languages_dir = None
    script_dir = Path(__file__).parent
    home_dir = Path.home()
    
    search_paths = [
        script_dir / "languages",  # Development/direct execution
        home_dir / ".local" / "share" / "detect-repo-language" / "languages",  # User install
        Path("/usr/share/detect-repo-language/languages"),  # Arch Linux standard
        Path("/usr/local/share/detect-repo-language/languages"),  # Local system install
    ]
    
    # Also check in the wheel data directory structure
    import site
    for site_dir in site.getsitepackages():
        search_paths.insert(0, Path(site_dir) / f"detect_repo_language-{VERSION}.data" / "data" / "languages")
    
    for path in search_paths:
        if path.is_dir():
            languages_dir = path
            break
    
    if not languages_dir:
        print(f"Error: {search_paths[0]} folder not found", file=sys.stderr)
        print(f"Searched in: {', '.join(str(p) for p in search_paths)}", file=sys.stderr)
        sys.exit(1)
    
    json_files = sorted(languages_dir.rglob("*.json"))
    json_files = [f for f in json_files if not f.stem[0].isupper()]
    if not json_files:
        print(f"Error: No language definitions found in {languages_dir}", file=sys.stderr)
        sys.exit(1)
    
    try:
        for config_file in json_files:
            lang_name = config_file.stem
            
            with open(config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if 'name' in data:
                lang_name = data['name']
            else:
                lang_name = lang_name.title()
            
            extensions = list(set(data.get('extensions', [])))
            LANGUAGE_EXTENSIONS[lang_name] = extensions
            LANGUAGE_GLYPHS[lang_name] = data.get('glyph', '')
            LANGUAGE_WEIGHTS[lang_name] = data.get('weight', 1.0)
            
            for ext in extensions:
                if ext.startswith('.'):
                    EXTENSION_MAP[ext] = lang_name
                else:
                    FILENAME_MAP[ext] = lang_name
    
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading language definitions: {e}", file=sys.stderr)
        sys.exit(1)