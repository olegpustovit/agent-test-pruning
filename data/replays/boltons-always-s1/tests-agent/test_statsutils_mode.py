from boltons import statsutils
from boltons.statsutils import Stats, mode


def test_numeric_mode():
    assert mode([2, 1, 3, 1]) == 1
    assert Stats([5, 5, 7]).mode == 5


def test_categorical_mode():
    assert mode(['a', 'b', 'b', 'c', 'c', 'c']) == 'c'


def test_tie_first_seen():
    assert mode([3, 3, 1, 1, 2]) == 3
    assert mode([1, 1, 2, 2, 3]) == 1
    assert mode(['x', 'y']) == 'x'


def test_unsorted_data_order_preserved():
    assert mode([9, 2, 2, 9, 1]) == 9


def test_single_and_generator():
    assert mode([4]) == 4
    assert mode(iter([1, 2, 2])) == 2


def test_empty_uses_default():
    assert Stats([], default=7).mode == 7


def test_module_function_exported():
    assert statsutils.mode is mode
    assert 'mode' in statsutils.__doc__
