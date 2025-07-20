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
# Build language map at module load
DEFAULT_LANGUAGE_MAP = build_language_map()

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

def main():
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
                   action='store_false',
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

    filename = args["file"][0]
    with open(filename) as code_pyfile:
        code = code_pyfile.read()

    # Default mode is 'lex' if not specified
    mode = args.get('mode', 'lex')
    
    return run_module(mode, code, args)

if __name__ == "__main__":
    sys.exit(main())