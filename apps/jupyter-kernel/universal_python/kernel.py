from ipykernel.kernelbase import Kernel

from ipykernel.ipkernel import IPythonKernel

from universalpython import run_module

import traceback

from io import StringIO
import sys
class UniversalPythonKernel(IPythonKernel):
    implementation = 'UniversalPython'
    implementation_version = '1.1'
    # language_version = '0.1'
    language_info = {
        'name': 'python',
        'version': sys.version.split()[0],
        'mimetype': 'text/x-python',
        'file_extension': '.py',
    }
    banner = "UniversalPython kernel"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_language = ""

    def get_language_and_code(self, code):
            lines = code.splitlines()
            lang = self.current_language
            if lines and lines[0].strip().startswith("# language:"):
                lang_flag = lines[0].strip().split(":", 1)[-1].strip()
                if lang_flag:
                    lang = lang_flag
                    self.current_language = lang  # persist for future cells
                    code = "\n".join(lines[1:])  # Remove the flag line
            return lang

    def do_execute(self, code, silent, store_history=True, user_expressions=None,
                   allow_stdin=False):
        error_thrown = False

        compiled_code = ""
        lang = self.get_language_and_code(code)

        try:
            compiled_code = run_module("lex", code, args = {
                            'translate': True,
                            'reverse': False,
                            'dictionary': '',
                            'source_language': lang,
                            'keep': False,         
                            'keep_only': False,
                            'return': True,
                            'file': '',
                            'suppress_warnings': True,  # Suppress warnings during compilation
                        })
        except Exception as e:
            error_thrown = True
            error_message = "Error while compiling code: " + str(e)
            print (error_message)

        return super(UniversalPythonKernel, self).do_execute(compiled_code, silent, store_history, user_expressions,
                   allow_stdin)


    def do_complete(self, code, cursor_pos):
        error_thrown = False

        lang = self.get_language_and_code(code)

        compiled_code = run_module("lex", code, args = {
            'translate': True,
            'reverse': False,
            'dictionary': '',
            'source_language': lang,
            'keep': False,         
            'keep_only': False,
            'return': True,
            'file': '',
            'suppress_warnings': True,  # Suppress warnings during compilation
        })

        return super(UniversalPythonKernel, self).do_complete(compiled_code, cursor_pos)