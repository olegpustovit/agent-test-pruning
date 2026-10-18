import pytest
from boltons.setutils import IndexedSet


def _make():
    s = IndexedSet(range(10))
    for v in (0, 1, 3):
        s.remove(v)
    return s


@pytest.mark.parametrize("sl", [
    slice(0, 3), slice(1, 4), slice(2, None), slice(None, 2), slice(None, None),
    slice(-3, None), slice(None, -2), slice(-4, -1), slice(-100, 3),
    slice(0, 100), slice(None, None, 2), slice(1, None, 2),
])
def test_slice_matches_list_after_removals(sl):
    s = _make()
    assert list(s[sl]) == list(s)[sl]


def test_slice_after_removal_explicit():
    s = _make()
    assert list(s[0:2]) == [2, 4]
    assert list(s[1:3]) == [4, 5]


def test_negative_step_uses_reversed_stream():
    s = _make()
    assert list(s[2:4:-1]) == list(reversed(list(s)))[2:4]
    assert list(s[::-1]) == list(s)[::-1]


def test_slice_after_pop_front():
    s = IndexedSet("abcdef")
    s.pop(0)
    s.pop(0)
    assert list(s[0:2]) == ["c", "d"]
    assert list(s[-2:]) == ["e", "f"]
