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
SCRIPTDIR = os.path.dirname(__file__)

def run_module(
        mode, 
        code,
        args={
            'translate': False,
            'dictionary': os.path.join(SCRIPTDIR, 'languages/ur/ur_native.lang.yaml'),
            'reverse': False,
            'keep': False,         
            'keep_only': False,
            'return': True,
        }, 
    ):
    mod = importlib.import_module(".modes."+mode, package='universalpython')
    return mod.run(args, code)

def main():
    import argparse

    # construct the argument parser and parse the argument
    ap = argparse.ArgumentParser()
    
    ap.add_argument('file', metavar='F', type=str, nargs='+',
                        help='File to compile.')

    ap.add_argument("-t", "--translate", 
                        action='store_true',
                        default=False, required = False, 
                        help = "Translate variables and functions to English, using the unicode.")
    ap.add_argument("-m", "--mode",
                        default="lex", required = False, 
                        help = "The mode to use to translate the code.")
    ap.add_argument("-d", "--dictionary",
                        default=os.path.join(SCRIPTDIR, 'languages/ur/ur_native.lang.yaml'), required = False, 
                        help = "The dictionary to use to translate the code.")

    ap.add_argument("-r", "--reverse",
                        action='store_true',
                        default=False, required = False, 
                        help = "Translate English code to the language of your choice.")


    ap.add_argument("-re", "--return",
                        action='store_false',
                        default=False, required = False, 
                        help = "Return the code instead of executing (used in module mode).")




    group = ap.add_mutually_exclusive_group(required=False)

    group.add_argument("-k", "--keep", 
                        action='store_true',
                        default=False, required = False, 
                        help = "Save the compiled file to the specified location.")
    group.add_argument("-ko", "--keep-only", 
                        action='store_true',
                        default=False, required = False, 
                        help = "Save the compiled file to the specified location, but don't run the file.")

    args = vars(ap.parse_args())

    code_pyfile = open(args["file"][0])
    code = code_pyfile.read()
    mode = args["mode"]

    run_module (mode, code, args)


if __name__ == "__main__":
    sys.exit(main())
