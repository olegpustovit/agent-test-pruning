import itertools

from boltons.iterutils import pairwise, pairwise_iter, windowed, windowed_iter


def test_pairwise_default_unchanged():
    assert pairwise(range(3)) == [(0, 1), (1, 2)]
    assert pairwise([]) == []
    assert pairwise([1]) == []


def test_pairwise_end():
    assert pairwise(range(3), end=None) == [(0, 1), (1, 2), (2, None)]
    assert list(pairwise_iter(range(3), end=None)) == [(0, 1), (1, 2), (2, None)]
    assert pairwise([1], end=0) == [(1, 0)]
    assert pairwise([], end=0) == []


def test_pairwise_end_none_vs_unset():
    # None is a legitimate end value, distinct from unset
    assert len(pairwise([1, 2], end=None)) == 2
    assert len(pairwise([1, 2])) == 1


def test_windowed_fill():
    assert windowed(range(4), 3, fill=None) == [
        (0, 1, 2), (1, 2, 3), (2, 3, None), (3, None, None)]
    assert list(windowed_iter(range(2), 4, fill='x')) == [
        (0, 1, 'x', 'x'), (1, 'x', 'x', 'x')]


def test_windowed_short_input():
    assert windowed(range(3), 5) == []
    assert windowed(range(3), 5, fill=0) == [
        (0, 1, 2, 0, 0), (1, 2, 0, 0, 0), (2, 0, 0, 0, 0)]
    assert windowed([], 3, fill=0) == []


def test_windowed_default_unchanged():
    assert windowed(range(7), 3) == [(i, i + 1, i + 2) for i in range(5)]


def test_infinite_iterators_fill_no_effect():
    got = list(itertools.islice(windowed_iter(itertools.count(), 3, fill=None), 3))
    assert got == [(0, 1, 2), (1, 2, 3), (2, 3, 4)]
    got = list(itertools.islice(pairwise_iter(itertools.count(), end=None), 2))
    assert got == [(0, 1), (1, 2)]
