import configparser
import os
import re

import boltons

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _read(*parts):
    with open(os.path.join(ROOT, *parts), encoding='utf-8') as f:
        return f.read()


def test_version_attribute_format():
    assert isinstance(boltons.__version__, str)
    assert re.match(r'^\d+\.\d+\.\d+(dev)?$', boltons.__version__)


def test_version_matches_source_literal():
    src = _read('boltons', '__init__.py')
    m = re.search(r"^__version__ = '(.*)'", src, re.M)
    assert m and m.group(1) == boltons.__version__


def test_pyproject_dynamic_version():
    text = _read('pyproject.toml')
    assert 'dynamic = ["version"]' in text
    assert not re.search(r'^version\s*=', text, re.M)
    assert '[dependency-groups]' in text
    assert re.search(r'^dev = \[', text, re.M)


def test_requirements_test_removed():
    assert not os.path.exists(os.path.join(ROOT, 'requirements-test.txt'))


def test_tox_ini_uses_uv_and_dependency_groups():
    cp = configparser.ConfigParser(interpolation=None)
    cp.read(os.path.join(ROOT, 'tox.ini'))
    assert cp['tox']['requires'].strip() == 'tox-uv'
    env = cp['testenv']
    assert env['dependency_groups'].strip() == 'dev'
    assert 'deps' not in env
    assert '{env_site_packages_dir}/boltons' in env['commands']
    assert '{tox_root}/tests' in env['commands']


def test_docs_conf_derives_version():
    src = _read('docs', 'conf.py')
    assert 'release = boltons.__version__' in src
    assert 'pprint' not in src
    release = boltons.__version__
    assert '.'.join(release.split('.')[:2]).count('.') == 1


def test_gitignore_has_dot_venv():
    assert '.venv/' in _read('.gitignore').splitlines()


def test_tests_workflow_uses_uv():
    text = _read('.github', 'workflows', 'tests.yaml')
    assert re.search(r'astral-sh/setup-uv@[0-9a-f]{40}', text)
    assert 'uvx --with tox-uv tox -e ${{ matrix.tox }}' in text
    assert 'pip install' not in text
    assert 'actions/cache' not in text


def test_publish_workflow_structure():
    text = _read('.github', 'workflows', 'publish.yml')
    assert '"[0-9]*.[0-9]*.[0-9]*"' in text
    for job in ('build:', 'publish:', 'verify:'):
        assert re.search(r'^  ' + job, text, re.M)
    assert 'id-token: write' in text
    assert re.search(r'pypa/gh-action-pypi-publish@[0-9a-f]{40}', text)
    assert 'needs: build' in text and 'needs: publish' in text
    assert 'uv build' in text


def test_publish_version_extraction_sed():
    # Run the sed expression used in the workflow against the real file.
    import shutil
    import subprocess
    if shutil.which('sed') is None:
        return
    text = _read('.github', 'workflows', 'publish.yml')
    assert """sed -n "s/^__version__ = '\\(.*\\)'/\\1/p" boltons/__init__.py""" in text
    out = subprocess.check_output(
        ['sed', '-n', r"s/^__version__ = '\(.*\)'/\1/p", 'boltons/__init__.py'],
        cwd=ROOT).decode().strip()
    assert out == boltons.__version__
