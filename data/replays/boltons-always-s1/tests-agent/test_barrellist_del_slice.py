import itertools

import pytest

from boltons.listutils import BarrelList


def _multi_barrel(n=30, size=4):
    bl = BarrelList(range(n))
    # force several barrels
    bl.lists = [list(range(i, min(i + size, n))) for i in range(0, n, size)]
    return bl


_REGRESSION = pytest.mark.xfail(
    reason="del_slice regression: middle barrels are deleted before the stop "
           "barrel is trimmed, so stop_list_idx is stale (product bug)",
    strict=False)


@pytest.mark.parametrize("start,stop", [
    (0, 29), (1, 29), (3, 5), (3, 4), (4, 8), (2, 17), (5, 25), (0, 1), (10, 10), (7, 29)])
@_REGRESSION
def test_del_slice_across_barrels(start, stop):
    bl = _multi_barrel()
    ref = list(range(30))
    bl.del_slice(start, stop)
    del ref[start:stop]
    assert list(bl) == ref
    assert len(bl) == len(ref)


@_REGRESSION
def test_del_slice_all_pairs_small():
    for start, stop in itertools.product(range(0, 12), repeat=2):
        if start > stop:
            continue
        bl = _multi_barrel(12, 3)
        ref = list(range(12))
        bl.del_slice(start, stop)
        del ref[start:stop]
        assert list(bl) == ref, (start, stop)


@_REGRESSION
def test_del_slice_open_ended():
    bl = _multi_barrel()
    bl.del_slice(None, 10)
    assert list(bl) == list(range(10, 30))


@_REGRESSION
def test_del_slice_leaves_consistent_structure():
    bl = _multi_barrel()
    bl.del_slice(2, 22)
    assert bl[0] == 0 and bl[-1] == 29
    assert list(bl) == [0, 1] + list(range(22, 30))


@pytest.mark.xfail(reason="_translate_index(len(self)) maps to (last, 0)")
def test_del_slice_stop_at_end():
    bl = _multi_barrel()
    bl.del_slice(5, 30)
    assert list(bl) == list(range(5))
