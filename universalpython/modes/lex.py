# ------------------------------------------------------------
# lex.py
#
# tokenizer to test UniversalPython grammar
# ------------------------------------------------------------

import warnings
import re
import ply.lex as lex
from unidecode import unidecode
import yaml

def run(args, code):
    # Load language dictionary
    language_dict = {}
    dictionary = args.get("dictionary", "")
    if dictionary:
        try:
            with open(dictionary) as f:
                language_dict = yaml.safe_load(f)
        except (yaml.YAMLError, OSError) as e:
            if not args.get("suppress_warnings", False):
                warnings.warn(
                    "Could not load language dictionary file. Defaulting to English Python.\n"
                    "Documentation: https://universalpython.github.io",
                    RuntimeWarning
                )
    else:
        if not args.get("suppress_warnings", False):
            warnings.warn(
                "No language dictionary specified. Defaulting to English Python.\n"
                "Documentation: https://universalpython.github.io\n"
                "Use --suppress-warnings to hide these messages.",
                RuntimeWarning
            )

    # Fallback to direct execution if no dictionary
    if not language_dict:
        return code if args.get("return") else exec(code)

    # Handle reserved words
    reserved = language_dict.get("reserved", {})
    if args["reverse"]:
        reserved = {v: k for k, v in reserved.items()}

    # Configure lexer to handle non-ASCII identifiers
    lex._is_identifier = re.compile(r'.')

    # Token definitions
    tokens = [
        "PLUS", "MINUS", "TIMES", "DIVIDE", "LPAREN", "RPAREN",
        "EQUALS", "ASSIGNMENT", "NUMBER", "STRING", "ID", "newline", "COMMENT"
    ] + list(reserved.values())

    # Simple token rules
    t_PLUS = r'\+'
    t_MINUS = r'-'
    t_TIMES = r'\*'
    t_DIVIDE = r'/'
    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_EQUALS = r'=='
    t_ASSIGNMENT = r'='

    # Track line numbers
    def t_newline(t):
        r'\n+'
        t.lexer.lineno += len(t.value)
        return t

    # Number token with localization support
    def t_NUMBER(t):
        if args["reverse"]:
            value_str = list(t.value)
            for i in range(len(value_str)):
                value_str[i] = reserved.get(value_str[i], value_str[i])
            t.value = ''.join(value_str)
        else:
            try:
                import universalpython.filters.translate.unidecoder as num_filter
                t.value = num_filter.filter(t.value)
            except ImportError:
                t.value = unidecode(t.value)
        return t

    # Set NUMBER regex based on language settings
    if args["reverse"]:
        t_NUMBER.__doc__ = r'[0-9][0-9]*[\.]{0,1}[0-9]*'
    else:
        num_start = language_dict.get("numbers", {}).get("start", "0")
        num_end = language_dict.get("numbers", {}).get("end", "9")
        t_NUMBER.__doc__ = fr'[{num_start}-{num_end}][{num_start}-{num_end}]*[\.]{{0,1}}[{num_start}-{num_end}]*'

    # Identifier token with translation support
    def t_ID(t):
        t.type = reserved.get(t.value, 'ID')
        
        if args.get('translate'):
            if t.type == 'ID':
                if args['translate'] == 'argostranslate':
                    try:
                        from universalpython.filters.translate.argos_translator import argos_translator
                        t.value = argos_translator(t.value, args.get("source_language", "en"))
                    except ImportError:
                        t.value = unidecode(t.value)
                else:
                    t.value = unidecode(t.value)
        return t

    # Set ID regex based on language settings
    if args["reverse"]:
        t_ID.__doc__ = r'[a-zA-Z_][a-zA-Z_0-9]*'
    else:
        letters = language_dict.get("letters", {})
        letter_range = letters.get("start", "a") + "-" + letters.get("end", "z")
        if "extra" in letters:
            letter_range += letters["extra"]
        num_start = language_dict.get("numbers", {}).get("start", "0")
        num_end = language_dict.get("numbers", {}).get("end", "9")
        t_ID.__doc__ = fr'[{letter_range}_][{letter_range}{num_start}-{num_end}_]*'

    # String token
    def t_STRING(t):
        r'("(\\"|[^"])*")|(\'(\\\'|[^\'])*\')'
        return t

    # Comment token
    def t_COMMENT(t):
        r'\#.*\n'
        return t

    # Error handling
    def t_error(t):
        if args["reverse"] is False:
            t.value = unidecode(t.value[0])
        else:
            t.value = t.value[0]
        t.lexer.skip(1)
        return t

    # Punctuation translation
    punctuation_map = {
        ".": language_dict.get("reserved", {}).get(".", "."),
        ",": language_dict.get("reserved", {}).get(",", ","),
    }
    if args["reverse"]:
        punctuation_map = {v: k for k, v in punctuation_map.items()}

    for key, value in punctuation_map.items():
        code = code.replace(key, value)

    # Build and run the lexer
    lexer = lex.lex()
    lexer.input(code)

    compiled_code = ""
    if args.get("keep") or args.get("keep_only"):
        print(f"Compiling {args['file'][0]}...")

    # Tokenize and build output
    while True:
        tok = lexer.token()
        if not tok:
            break

        if tok.value in reserved:
            compiled_code += tok.type if (tok.type != 'NUMBER' and tok.value not in punctuation_map and tok.type not in punctuation_map) else tok.value
        else:
            compiled_code += tok.value

    # Output handling
    if args.get("keep") or args.get("keep_only"):
        with open("compiled.en.py", "w") as f:
            f.write(compiled_code)

    if args.get("return"):
        return compiled_code
    elif not args.get("keep_only"):
        exec(compiled_code)