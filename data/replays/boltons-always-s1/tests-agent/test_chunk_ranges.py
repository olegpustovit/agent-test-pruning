import pytest

from boltons.iterutils import chunk_ranges, chunked_iter


def cr(*a, **kw):
    return list(chunk_ranges(*a, **kw))


def test_basic():
    assert cr(input_offset=10, input_size=10, chunk_size=5) == [(10, 15), (15, 20)]
    assert cr(10, 3) == [(0, 3), (3, 6), (6, 9), (9, 10)]


def test_overlap():
    assert cr(10, 5, 10, 1) == [(10, 15), (14, 19), (18, 20)]
    assert cr(10, 5, 10, 2) == [(10, 15), (13, 18), (16, 20)]


def test_align():
    assert cr(15, 5, 4, align=False) == [(4, 9), (9, 14), (14, 19)]
    assert cr(15, 5, 4, align=True) == [(4, 5), (5, 10), (10, 15), (15, 19)]
    assert cr(15, 5, 2, 1, align=False) == [(2, 7), (6, 11), (10, 15), (14, 17)]
    assert cr(15, 5, 2, 1, align=True) == [(2, 5), (4, 9), (8, 13), (12, 17)]
    assert cr(15, 5, 3, 1, align=True) == [(3, 5), (4, 9), (8, 13), (12, 17), (16, 18)]


def test_align_already_aligned():
    assert cr(10, 5, 5, align=True) == [(5, 10), (10, 15)]


def test_align_short_input():
    assert cr(2, 5, 1, align=True) == [(1, 3)]


def test_empty_and_small():
    assert cr(0, 5) == []
    assert cr(3, 5) == [(0, 3)]
    assert cr(5, 5) == [(0, 5)]


def test_is_iterator():
    assert iter(chunk_ranges(5, 2)) is not None
    assert next(chunk_ranges(5, 2)) == (0, 2)


@pytest.mark.parametrize('kw', [
    dict(input_size=-1, chunk_size=1),
    dict(input_size=1, chunk_size=0),
    dict(input_size=1, chunk_size=-1),
    dict(input_size=1, chunk_size=1, input_offset=-1),
    dict(input_size=1, chunk_size=1, overlap_size=-1),
])
def test_invalid(kw):
    with pytest.raises(ValueError):
        cr(**kw)


def test_chunked_iter_validation_preserved():
    with pytest.raises(ValueError):
        list(chunked_iter([1, 2], 0))
    with pytest.raises(ValueError):
        list(chunked_iter([1, 2], -1))
    assert list(chunked_iter([1, 2, 3], 2)) == [[1, 2], [3]]
