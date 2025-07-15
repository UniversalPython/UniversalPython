# -*- coding: utf-8 -*-
from universalpython import run_module

print ("Imported successfully.")

import os

code = r"""

کچھ = ۱
لکھو("سلام دنیا")

"""

compiled_code = run_module(
    mode = "lex", 
    code = code,
    args = {
        'translate': False,
        'dictionary': '../languages/ur/ur_native.lang.yaml',
        'reverse': False,
        'keep': False,         
        'keep_only': False,
        'return': True,
    }, 
    )
print ("Original code is:\n", code)
print ('--------------------------------')
print ("Compiled code is:\n", compiled_code)