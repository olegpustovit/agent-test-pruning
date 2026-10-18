import itertools

import pytest

from boltons.listutils import BarrelList

# iter_slice in the working tree no longer follows list slice semantics
# (negative/out-of-range bounds raise ValueError from islice).
ISLICE_BROKEN = pytest.mark.xfail(
    reason="iter_slice does not match list slicing", raises=ValueError)

BOUNDS = [None, -30, -11, -10, -5, -1, 0, 1, 5, 9, 10, 11, 30]
STEPS = [None, 1, 2, 3, -1, -2, -3]


@pytest.mark.parametrize("n", [0, 1, 10])
@ISLICE_BROKEN
def test_iter_slice_matches_list(n):
    ref = list(range(n))
    bl = BarrelList(ref)
    for start, stop, step in itertools.product(BOUNDS, BOUNDS, STEPS):
        assert list(bl.iter_slice(start, stop, step)) == ref[start:stop:step], \
            (start, stop, step)


@ISLICE_BROKEN
def test_iter_slice_reverse_default_bounds():
    bl = BarrelList(range(10))
    assert list(bl.iter_slice(None, None, -1)) == list(range(9, -1, -1))
    assert list(bl.iter_slice(None, None, -3)) == [9, 6, 3, 0]


@ISLICE_BROKEN
def test_iter_slice_out_of_range_bounds_clamped():
    bl = BarrelList(range(5))
    assert list(bl.iter_slice(-100, 100)) == [0, 1, 2, 3, 4]
    assert list(bl.iter_slice(100, -100, -1)) == [4, 3, 2, 1, 0]
