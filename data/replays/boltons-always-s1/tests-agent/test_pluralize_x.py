import pytest

from boltons.strutils import pluralize


@pytest.mark.parametrize('word, plural', [
    ('box', 'boxes'),
    ('fox', 'foxes'),
    ('tax', 'taxes'),
    ('Box', 'Boxes'),
    ('BOX', 'BOXES'),
    ('x', 'xes'),
    ('ox', 'oxen'),
    ('boxes', 'boxes'),
    ('bus', 'buses'),
    ('church', 'churches'),
    ('dish', 'dishes'),
    ('cat', 'cats'),
])
def test_pluralize_x(word, plural):
    assert pluralize(word) == plural
