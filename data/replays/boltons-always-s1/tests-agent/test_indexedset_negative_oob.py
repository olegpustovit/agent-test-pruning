import pytest

from boltons.setutils import IndexedSet


def test_getitem_negative_out_of_range():
    s = IndexedSet('abc')
    assert s[-3] == 'a'
    for i in (-4, -5, -100):
        with pytest.raises(IndexError):
            s[i]


def test_getitem_positive_out_of_range():
    s = IndexedSet('abc')
    with pytest.raises(IndexError):
        s[3]


def test_getitem_empty():
    for i in (0, -1):
        with pytest.raises(IndexError):
            IndexedSet()[i]


def test_getitem_negative_oob_with_dead_indices():
    s = IndexedSet(range(6))
    s.remove(1)
    s.remove(2)
    assert list(s) == [0, 3, 4, 5]
    assert s[-4] == 0
    with pytest.raises(IndexError):
        s[-5]
    with pytest.raises(IndexError):
        s[4]


def test_pop_negative_out_of_range_leaves_set_intact():
    s = IndexedSet('abc')
    with pytest.raises(IndexError):
        s.pop(-4)
    with pytest.raises(IndexError):
        s.pop(3)
    assert list(s) == ['a', 'b', 'c']
    assert s.pop(-3) == 'a'
    assert list(s) == ['b', 'c']


def test_pop_negative_oob_with_dead_indices():
    s = IndexedSet(range(5))
    s.remove(0)
    with pytest.raises(IndexError):
        s.pop(-5)
    assert list(s) == [1, 2, 3, 4]
