import pytest

from boltons import strutils
from boltons.strutils import removeprefix


@pytest.mark.parametrize('text, prefix, expected', [
    ('foobar', 'foo', 'bar'),
    ('foobar', 'bar', 'foobar'),
    ('foobar', '', 'foobar'),
    ('foo', 'foo', ''),
    ('foo', 'foobar', 'foo'),
    ('', 'foo', ''),
    ('', '', ''),
    ('foofoo', 'foo', 'foo'),
    ('Foobar', 'foo', 'Foobar'),
])
def test_removeprefix(text, prefix, expected):
    assert removeprefix(text, prefix) == expected


def test_exported():
    assert 'removeprefix' in strutils.__all__
