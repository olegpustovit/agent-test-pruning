import pytest

from boltons.listutils import BarrelList
from boltons.setutils import IndexedSet, _MAX_DEAD_INTERVALS


def _big(n=3000):
    return IndexedSet(range(n))


def test_difference_update_bulk():
    s = _big()
    other = set(range(0, 3000, 2))
    assert len(other) > _MAX_DEAD_INTERVALS
    s.difference_update(other)
    assert list(s) == list(range(1, 3000, 2))
    assert s.index(1) == 0 and s.index(2999) == 1499
    assert 2 not in s and 3 in s
    assert s.dead_indices == []
    s.add(4)
    assert list(s)[-1] == 4


def test_intersection_update_bulk():
    s = _big()
    keep = set(range(0, 3000, 3))
    s.intersection_update(keep)
    assert list(s) == list(range(0, 3000, 3))
    assert s.index(9) == 3
    assert s.dead_indices == []


def test_bulk_after_prior_removals():
    s = _big()
    s.discard(5)
    s.pop(0)
    s.difference_update(set(range(10, 2000)))
    assert list(s) == [1, 2, 3, 4, 6, 7, 8, 9] + list(range(2000, 3000))
    assert s.index(2000) == 8


def test_small_update_still_works():
    s = _big(100)
    s.difference_update({1, 2, 3})
    assert 1 not in s and len(s) == 97
    s.intersection_update({0, 4, 5})
    assert list(s) == [0, 4, 5]


def test_barrel_insert_clamps():
    for idx, expected in [(100, 'end'), (-100, 'start')]:
        bl = BarrelList(range(10))
        bl.lists = [[0, 1, 2], [3, 4, 5], [6, 7, 8, 9]]
        ref = list(range(10))
        bl.insert(idx, 'x')
        ref.insert(idx, 'x')
        assert list(bl) == ref
    bl = BarrelList(range(10))
    bl.lists = [[0, 1, 2], [3, 4, 5], [6, 7, 8, 9]]
    bl.insert(10, 'x')
    assert list(bl)[-1] == 'x'


def test_barrel_translate_index_out_of_range():
    bl = BarrelList(range(5))
    assert bl._translate_index(5) == (None, None)
    assert bl._translate_index(50) == (None, None)
    assert bl._translate_index(4) == (0, 4)


def test_barrel_pop_removes_empty_sublist():
    bl = BarrelList()
    bl.lists = [[0], [1, 2], [3]]
    assert bl.pop(0) == 0
    assert bl.lists[0] != []
    assert list(bl) == [1, 2, 3]


def test_barrel_pop_last_skips_empty_tail():
    bl = BarrelList()
    bl.lists = [[1, 2], [], []]
    assert bl.pop() == 2
    assert list(bl) == [1]
    with pytest.raises(IndexError):
        BarrelList().pop(3)
