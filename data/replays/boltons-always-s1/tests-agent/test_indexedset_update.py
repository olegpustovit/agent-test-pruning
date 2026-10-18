from boltons.setutils import IndexedSet


def test_update_multiple_iterables_flattens():
    s = IndexedSet([0])
    s.update([1, 2], [3, 4])
    assert list(s) == [0, 1, 2, 3, 4]


def test_update_three_iterables_with_overlap():
    s = IndexedSet()
    s.update('ab', 'bc', 'cd')
    assert list(s) == ['a', 'b', 'c', 'd']


def test_update_single_iterable():
    s = IndexedSet([1])
    s.update([2, 3])
    assert list(s) == [1, 2, 3]


def test_update_multiple_with_tuple_elements():
    s = IndexedSet()
    s.update([(1, 2)], [(3, 4)])
    assert list(s) == [(1, 2), (3, 4)]


def test_update_no_args():
    s = IndexedSet([1])
    s.update()
    assert list(s) == [1]
