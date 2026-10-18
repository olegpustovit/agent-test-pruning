import random

from boltons.listutils import BarrelList


def _multi(data):
    bl = BarrelList()
    bl.lists = [list(data[i:i + 3]) for i in range(0, len(data), 3)]
    return bl


def test_sort_multiple_lists():
    data = [9, 3, 7, 1, 8, 2, 6, 4, 5, 0, 11, 10]
    bl = _multi(data)
    assert len(bl.lists) > 1
    bl.sort()
    assert list(bl) == sorted(data)
    assert len(bl) == len(data)


def test_sort_large_random():
    random.seed(1)
    data = [random.randint(0, 1000) for _ in range(3000)]
    bl = BarrelList(data)
    bl.sort()
    assert list(bl) == sorted(data)


def test_sort_single_list():
    bl = BarrelList([3, 1, 2])
    bl.sort()
    assert list(bl) == [1, 2, 3]
