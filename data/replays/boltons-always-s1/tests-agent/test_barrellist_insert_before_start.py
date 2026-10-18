from boltons.listutils import BarrelList


def _multi():
    bl = BarrelList()
    bl.lists = [[1, 2], [3, 4]]
    return bl


def test_insert_before_start_multi_list():
    bl = _multi()
    bl.insert(-100, 'x')
    assert list(bl) == ['x', 1, 2, 3, 4]


def test_insert_before_start_matches_list():
    bl, ref = _multi(), [1, 2, 3, 4]
    bl.insert(-7, 'x')
    ref.insert(-7, 'x')
    assert list(bl) == ref


def test_insert_in_range_negative_still_works():
    bl = _multi()
    bl.insert(-1, 'x')
    assert list(bl) == [1, 2, 3, 'x', 4]
