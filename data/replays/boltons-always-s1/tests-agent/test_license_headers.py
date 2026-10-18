import ast
import glob
import importlib
import os

import pytest

BOLTONS_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'boltons')
MODULES = sorted(os.path.basename(p)[:-3]
                 for p in glob.glob(os.path.join(BOLTONS_DIR, '*utils.py')))
MODULES = [m for m in MODULES if m != 'cacheutils_placeholder']

HEADER_LINES = [
    '# Copyright (c) 2013, Mahmoud Hashemi',
    '# Redistribution and use in source and binary forms, with or without',
    '#    * The names of the contributors may not be used to endorse or',
    '# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS',
    '# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.',
]


def _read(name):
    with open(os.path.join(BOLTONS_DIR, name + '.py'), encoding='utf-8') as f:
        return f.read()


def test_modules_found():
    assert len(MODULES) >= 29


@pytest.mark.parametrize('name', MODULES)
def test_license_header_present(name):
    src = _read(name)
    head = src.split('"""')[0] if '"""' in src else src
    lines = src.splitlines()
    for expected in HEADER_LINES:
        assert expected in lines, (name, expected)
    # header precedes any code
    first_code = next(i for i, l in enumerate(lines)
                      if l.strip() and not l.startswith('#'))
    last_header = lines.index(HEADER_LINES[-1])
    assert last_header < first_code


@pytest.mark.parametrize('name', MODULES)
def test_module_still_parses_and_imports(name):
    ast.parse(_read(name))
    mod = importlib.import_module('boltons.' + name)
    assert mod.__doc__ is None or isinstance(mod.__doc__, str)


@pytest.mark.parametrize('name', MODULES)
def test_docstring_preserved(name):
    # The license comment must not displace the module docstring.
    src = _read(name)
    tree = ast.parse(src)
    mod = importlib.import_module('boltons.' + name)
    assert mod.__doc__ == ast.get_docstring(tree, clean=False)
