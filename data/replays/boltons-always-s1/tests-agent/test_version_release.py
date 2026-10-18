import re
from pathlib import Path

import boltons

ROOT = Path(__file__).resolve().parents[2]


def test_version_is_dev():
    assert boltons.__version__ == '26.2.1dev'
    assert re.fullmatch(r'\d{2}\.\d+\.\d+dev', boltons.__version__)


def test_changelog_26_2_0_dated_and_first():
    text = (ROOT / 'CHANGELOG.md').read_text(encoding='utf-8')
    section = text.split('## 26.2.0', 1)[1].split('## 26.1.0', 1)[0]
    assert '_(September 7, 2026)_' in section
    assert 'unreleased' not in section
    assert text.index('## 26.2.0') < text.index('## 26.1.0')


def test_changelog_has_26_1_0_first():
    text = (ROOT / 'CHANGELOG.md').read_text(encoding='utf-8')
    assert '## 26.1.0\n' in text
    assert text.index('## 26.1.0') < text.index('## 26.0.0')


def test_changelog_lists_latest_release_first():
    text = (ROOT / 'CHANGELOG.md').read_text(encoding='utf-8')
    assert '## 26.0.0\n' in text
    assert text.index('## 26.0.0') < text.index('## 25.0.0')


def test_changelog_link_refs_defined():
    text = (ROOT / 'CHANGELOG.md').read_text(encoding='utf-8')
    section = text.split('## 26.0.0', 1)[1].split('## 25.0.0', 1)[0]
    for ref in set(re.findall(r'\]\[([^\]]+)\]', section)):
        assert re.search(r'^\[%s\]: http' % re.escape(ref), text, re.M), ref
