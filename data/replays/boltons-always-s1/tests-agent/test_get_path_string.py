import pytest
from boltons.iterutils import get_path, PathAccessError

ROOT = {'a': {'b': [10, {'c': 3}]}, 'x.y': 1}


def test_dotted_string_matches_tuple():
    assert get_path(ROOT, 'a.b') == get_path(ROOT, ('a', 'b'))
    assert get_path(ROOT, 'a.b.1.c') == 3


def test_dotted_string_list_index():
    assert get_path(ROOT, 'a.b.0') == 10


def test_dotted_string_missing_default():
    assert get_path(ROOT, 'a.z', default=None) is None
    with pytest.raises(PathAccessError):
        get_path(ROOT, 'a.z')


def test_single_segment_string():
    assert get_path(ROOT, 'a') is ROOT['a']


def test_tuple_keeps_dots_literal():
    assert get_path(ROOT, ('x.y',)) == 1
