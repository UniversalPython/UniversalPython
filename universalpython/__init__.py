#!/usr/bin/env python

"""
UniversalPython.

Python, but in different human languages.
"""

from importlib.metadata import version as get_version, PackageNotFoundError

try:
    __version__ = get_version("universalpython")
except PackageNotFoundError:
    __version__ = "0.0.0"

__author__ = 'Saad Bazaz'
__credits__ = 'Grayhat'
__url__ = 'https://github.com/UniversalPython/UniversalPython'

from .universalpython import *
