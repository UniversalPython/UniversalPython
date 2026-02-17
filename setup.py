from setuptools import setup
import os
import yaml

LANGUAGES_DIR = os.path.join(os.path.dirname(__file__), 'universalpython', 'languages')

def get_aliases():
    aliases = []
    if not os.path.exists(LANGUAGES_DIR):
        return aliases
    for lang_dir in os.listdir(LANGUAGES_DIR):
        yaml_path = os.path.join(LANGUAGES_DIR, lang_dir, 'default.yaml')
        if not os.path.isfile(yaml_path):
            continue
        with open(yaml_path, encoding='utf-8') as f:
            data = yaml.safe_load(f)
        for alias in data.get('aliases', []):
            aliases.append(f'{alias}=universalpython.universalpython:main')
    return aliases

console_scripts = [
    'universalpython=universalpython.universalpython:main',
    'unipy=universalpython.universalpython:main',
] + get_aliases()

setup(
    entry_points={
        'console_scripts': console_scripts,
    }
)