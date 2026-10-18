import pytest

from boltons.strutils import human_readable_list as hrl


def test_empty():
    assert hrl([]) == ''
    assert hrl(()) == ''


def test_single():
    assert hrl(['a']) == 'a'


def test_two():
    assert hrl(['a', 'b']) == 'a and b'
    assert hrl(['a', 'b'], oxford=False) == 'a and b'


def test_three_oxford_default():
    assert hrl(['a', 'b', 'c']) == 'a, b, and c'


def test_three_no_oxford():
    assert hrl(['a', 'b', 'c'], oxford=False) == 'a, b and c'


def test_many():
    assert hrl(list('abcd')) == 'a, b, c, and d'


def test_custom_conjunction():
    assert hrl(['a', 'b', 'c'], conjunction='or') == 'a, b, or c'
    assert hrl(['a', 'b'], conjunction='or') == 'a or b'


def test_custom_delimiter_and_whitespace_stripping():
    assert hrl(['a', 'b', 'c'], delimiter=';') == 'a; b; and c'
    assert hrl(['a', 'b', 'c'], delimiter=' ; ', conjunction=' or ') == 'a; b; or c'


def test_oxford_keyword_only():
    with pytest.raises(TypeError):
        hrl(['a', 'b', 'c'], ',', 'and', False)
