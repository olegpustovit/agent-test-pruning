import pytest
from boltons.iterutils import partition


def test_default_bool():
    assert partition(['', 'a', '', 'b']) == (['a', 'b'], ['', ''])


def test_single_predicate_returns_tuple_of_lists():
    res = partition(range(6), lambda i: i % 2 == 0)
    assert isinstance(res, tuple)
    assert res == ([0, 2, 4], [1, 3, 5])


def test_multiple_predicates():
    pos, neg, zero = partition(range(-2, 3), lambda i: i > 0, lambda i: i < 0)
    assert (pos, neg, zero) == ([1, 2], [-2, -1], [0])


def test_first_match_wins_and_order_preserved():
    a, b, rest = partition(range(10), lambda i: i % 2 == 0, lambda i: i % 3 == 0)
    assert a == [0, 2, 4, 6, 8]
    assert b == [3, 9]
    assert rest == [1, 5, 7]


def test_empty_source():
    assert partition([], bool, bool) == ([], [], [])


def test_string_key_uses_attribute():
    class O:
        def __init__(self, x):
            if x:
                self.flag = True
    objs = [O(1), O(0), O(1)]
    yes, no = partition(objs, 'flag')
    assert yes == [objs[0], objs[2]] and no == [objs[1]]


def test_generator_source():
    assert partition((i for i in range(4)), lambda i: i > 1) == ([2, 3], [0, 1])


def test_non_iterable_raises():
    with pytest.raises(TypeError):
        partition(5)


def test_bad_key_raises():
    with pytest.raises(TypeError):
        partition([1], 5)
    with pytest.raises(TypeError):
        partition([1], bool, 5)
