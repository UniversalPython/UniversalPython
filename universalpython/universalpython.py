# ------------------------------------------------------------
# universalpython.py
#
# Main driver file. 
# - Arguments are captured here
# - The parsing mode is called from here with the same args as this file
# ------------------------------------------------------------
import importlib
import inspect
import sys
import os
import re
import subprocess
import yaml

SCRIPTDIR = os.path.dirname(__file__)
LANGUAGES_DIR = os.path.join(SCRIPTDIR, 'languages')

def build_language_map():
    """Build language map in the format {lang: {filename: fullpath}}"""
    language_map = {}
    
    if not os.path.exists(LANGUAGES_DIR):
        return language_map
    
    for lang_dir in os.listdir(LANGUAGES_DIR):
        lang_path = os.path.join(LANGUAGES_DIR, lang_dir)
        if not os.path.isdir(lang_path):
            continue
            
        lang_files = {}
        for filename in os.listdir(lang_path):
            if filename.endswith('.yaml'):
                filepath = os.path.join(lang_path, filename)
                if os.path.isfile(filepath):
                    name = os.path.splitext(filename)[0]  # Remove .yaml
                    lang_files[name] = filepath
        
        if lang_files:  # Only add if we found YAML files
            language_map[lang_dir] = lang_files
            
    return language_map

def build_alias_map():
    """Build a map of {alias_name: lang_code} from language YAML files."""
    alias_map = {}
    for lang_code, lang_files in DEFAULT_LANGUAGE_MAP.items():
        if 'default' not in lang_files:
            continue
        with open(lang_files['default'], encoding='utf-8') as f:
            data = yaml.safe_load(f)
        for alias in data.get('aliases', []):
            alias_map[alias] = lang_code
    return alias_map

# Build language map at module load
DEFAULT_LANGUAGE_MAP = build_language_map()
DEFAULT_ALIAS_MAP = build_alias_map()

UP_FLAGS = {
    '-t',  '--translate',
    '-d',  '--dictionary',
    '-sl', '--source-language',
    '-r',  '--reverse',
    '-re', '--return',
    '-k',  '--keep',
    '-ko', '--keep-only',
    '-o',  '--options',
}

def detect_language_from_filename(filename):
    """Detect language from file extension (e.g., my-program.de.py -> german)
    Returns tuple: (filepath, two_letter_code) or None"""
    parts = filename.split('.')
    
    if len(parts) > 2:  # Has language code in extension
        lang_code = parts[-2].lower()
        if lang_code in DEFAULT_LANGUAGE_MAP:
            # Return first filepath found and the language code
            lang_files = DEFAULT_LANGUAGE_MAP[lang_code]
            first_file = next(iter(lang_files.values())) if lang_files else None
            return (first_file, lang_code)
    return None

def detect_language_from_comment(code):
    """Detect language from comment (e.g., # language:fr)
    Returns tuple: (filepath, two_letter_code) or None"""
    first_lines = code.split('\n')[:5]  # Check first 5 lines for comment
    for line in first_lines:
        match = re.search(r'^#\s*language\s*:\s*(\w+)', line, re.IGNORECASE)
        if match:
            lang_code = match.group(1).lower()
            if lang_code in DEFAULT_LANGUAGE_MAP:
                # Return first filepath found and the language code
                lang_files = DEFAULT_LANGUAGE_MAP[lang_code]
                first_file = next(iter(lang_files.values())) if lang_files else None
                return (first_file, lang_code)
    return None

def detect_language_from_alias(invoked_name):
    """Detect language from command alias.
    Returns: (filepath, lang_code) or None"""
    command = os.path.basename(invoked_name).lower()
    lang_code = DEFAULT_ALIAS_MAP.get(command)
    
    if lang_code and lang_code in DEFAULT_LANGUAGE_MAP:
        lang_files = DEFAULT_LANGUAGE_MAP[lang_code]
        first_file = next(iter(lang_files.values())) if lang_files else None
        return (first_file, lang_code)
    return None

def determine_language(args, filename, code):
    """Determine target language based on priority rules"""
    detected_dictionary = None
    
    detected_lang = None

    # Check detection methods in priority order
    if args.get('dictionary'):
        detected_dictionary = args['dictionary']
    elif args.get('source_language'):
        detected_dictionary = DEFAULT_LANGUAGE_MAP.get(args['source_language'], {})['default']
    else:
        detected_dictionary, detected_lang = (detect_language_from_comment(code) or 
                                     detect_language_from_filename(filename) or 
                                     detect_language_from_alias(sys.argv[0]) or
                                     (None, None))

    # Update source_language with the detected language if not explicitly set
    # if not args.get('source_language') and detected_lang:
    if detected_lang:
        args['source_language'] = detected_lang

    return detected_dictionary or ""

def run_module(
        mode, 
        code,
        args={
            'translate': False,
            'dictionary': "",
            'source_language': "",
            'reverse': False,
            'keep': False,         
            'keep_only': False,
            'return': True,
        }, 
    ):
    
    # Determine language and update source_language
    filename = ""
    if args["file"]: 
        filename = args["file"][0]
    args['dictionary'] = determine_language(args, filename, code)
        
    # Default mode is 'lex' if not specified
    mode = args.get('mode', 'lex')

    mod = importlib.import_module(".modes."+mode, package='universalpython')
    return mod.run(args, code)

def passthrough_to_python():
    """Replace this process with the real Python interpreter, forwarding all args."""
    if os.name == 'nt':
        sys.exit(subprocess.call([sys.executable] + sys.argv[1:]))
    os.execvp(sys.executable, [sys.executable] + sys.argv[1:])


def print_version():
    """Print UniversalPython version alongside the Python version."""
    try:
        from importlib.metadata import version as get_version
        up_version = get_version("universalpython")
    except Exception:
        up_version = "dev"
    py_version = sys.version.split()[0]
    print(f"UniversalPython {up_version}  (Python {py_version})")


def print_help():
    """Print UP-specific help, noting that unknown flags pass through to Python."""
    print(
        "UniversalPython \u2014 Python, but in your native language.\n"
        "\n"
        "Usage:\n"
        "  universalpython <file>              Compile & run a UniversalPython file\n"
        "  universalpython --options <file>     Compile & run a UP file (explicit)\n"
        "  universalpython --version | -V      Show UP + Python version\n"
        "  universalpython --help | -h         Show this help message\n"
        "\n"
        "UP compile options:\n"
        "  -o,  --options <file>        Compile & run a UniversalPython file\n"
        "  -t,  --translate [engine]   Translate identifiers (unidecode | argostranslate)\n"
        "  -d,  --dictionary <path>    Path to language dictionary YAML\n"
        "  -sl, --source-language <code>  Source language code (e.g. fr, de)\n"
        "  -r,  --reverse              Reverse-translate (English \u2192 target language)\n"
        "  -re, --return               Return compiled code instead of executing\n"
        "  -k,  --keep                 Save compiled .en.py file and run\n"
        "  -ko, --keep-only            Save compiled .en.py file without running\n"
        "\n"
        "Anything else (e.g. -c, -m, script.py) is forwarded to Python as-is."
    )


def main():
    cli_args = sys.argv[1:]

    if not cli_args:
        passthrough_to_python()
        return

    first = cli_args[0]

    if first in ('--version', '-V'):
        print_version()
        return

    if first in ('--help', '-h'):
        print_help()
        return

    if first in ('--options', '-o'):
        if len(cli_args) < 2:
            print("Error: --options requires a filename.")
            return
        filename = cli_args[1]
        try:
            with open(filename, encoding='utf-8') as f:
                code = f.read()
        except FileNotFoundError:
            print(f"Error: file not found: {filename}")
            return
        args = {
            'file': [filename],
            'translate': False,
            'dictionary': "",
            'source_language': "",
            'reverse': False,
            'keep': False,
            'keep_only': False,
            'return': False,
        }
        return run_module('lex', code, args)

    if first.startswith('-') and first not in UP_FLAGS:
        passthrough_to_python()
        return

    import argparse

    # construct the argument parser and parse the argument
    ap = argparse.ArgumentParser()
    
    ap.add_argument('file', metavar='F', type=str, nargs='+',
                   help='File to compile.')

    ap.add_argument("-t", "--translate", 
                   choices=["", "argostranslate", "unidecode"],
                   const="",  # Default when --translate is used without value
                   default=None,  # Default when --translate is not used at all
                   nargs='?',  # Makes the argument optional
                   required=False, 
                   help="Translate variables and functions. Options: "
                        "no value (unidecode), 'argostranslate', or 'unidecode'")
    
    ap.add_argument("-d", "--dictionary",
                   default="", required=False, 
                   help="The dictionary to use to translate the code.")

    ap.add_argument("-sl", "--source-language",
                   default="", required=False, 
                   dest="source_language",
                   help="The source language of the code (for translation).")
    
    ap.add_argument("-r", "--reverse",
                   action='store_true',
                   default=False, required=False, 
                   help="Translate English code to the language of your choice.")

    ap.add_argument("-re", "--return",
                   action='store_true',
                   default=False, required=False, 
                   help="Return the code instead of executing (used in module mode).")

    group = ap.add_mutually_exclusive_group(required=False)

    group.add_argument("-k", "--keep", 
                      action='store_true',
                      default=False, required=False, 
                      help="Save the compiled file to the specified location.")
    group.add_argument("-ko", "--keep-only", 
                      action='store_true',
                      default=False, required=False, 
                      help="Save the compiled file to the specified location, but don't run the file.")

    args = vars(ap.parse_args())

    if args['dictionary']:
        args['dictionary'] = os.path.abspath(args['dictionary'])

    filename = args["file"][0]
    with open(filename, encoding='utf-8') as code_pyfile:
        code = code_pyfile.read()

    # Default mode is 'lex' if not specified
    mode = args.get('mode', 'lex')
    
    return run_module(mode, code, args)

if __name__ == "__main__":
    sys.exit(main())