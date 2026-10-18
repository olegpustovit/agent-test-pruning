import pytest

from boltons import iterutils

STRIP_FUNCS = ['lstrip', 'lstrip_iter', 'rstrip', 'rstrip_iter', 'strip', 'strip_iter']


@pytest.mark.parametrize('name', STRIP_FUNCS)
def test_strip_docstring_spelling(name):
    doc = getattr(iterutils, name).__doc__
    assert 'analogous' in doc
    assert 'analigous' not in doc


def test_strip_behavior_unchanged():
    assert iterutils.lstrip(['Foo', 'Bar', 'Bam'], 'Foo') == ['Bar', 'Bam']
    assert iterutils.rstrip(['Foo', 'Bar', 'Bam'], 'Bam') == ['Foo', 'Bar']
    assert iterutils.strip(['Fu', 'Foo', 'Fu'], 'Fu') == ['Foo']
    assert list(iterutils.strip_iter(['Fu', 'Foo', 'Fu'], 'Fu')) == ['Foo']
