# References:
# - https://stackoverflow.com/questions/27494758/how-do-i-make-a-python-script-executable

import os
from setuptools import setup, find_packages

files = ["samples/*/*", "languages/*/*.yaml"]


# with open('requirements.txt') as f:
#     _required = f.read().splitlines()
#     required = []
#     for line in _required:
#         required.append(line.split('==', 1)[0])

setup(
    name='universalpython',
    version='0.0.3',
    author='Saad Bazaz',
    author_email='saadbazaz@hotmail.com',
    url='https://github.com/grayhatdevelopers/UniversalPython',

    install_requires=[
        "ply",
        "PyYAML",
        "Unidecode",
    ],

    # packages=['urdupython', 'modes', 'filters', 'languages'],
    packages=find_packages(),
    package_data = {'urdupython' : files },

    entry_points={
        'console_scripts': [
            'universalpython=urdupython.urdu_python:main',
            'urdupython=urdupython.urdu_python:main',
            'اردوپایتھان=urdupython.urdu_python:main',
            'اردوپای=urdupython.urdu_python:main'
        ]
    }
)
