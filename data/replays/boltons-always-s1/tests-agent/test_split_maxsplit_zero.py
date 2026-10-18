from boltons.iterutils import split, split_iter


def test_split_iter_maxsplit_zero_list():
    assert list(split_iter([1, None, 2], maxsplit=0)) == [[1, None, 2]]


def test_split_iter_maxsplit_zero_generator():
    assert list(split_iter((x for x in [1, 2, 3]), sep=2, maxsplit=0)) == [[1, 2, 3]]


def test_split_iter_maxsplit_zero_string():
    assert list(split_iter('abc', sep='b', maxsplit=0)) == [['a', 'b', 'c']]


def test_split_maxsplit_zero_empty():
    assert split([], maxsplit=0) == [[]]


def test_split_maxsplit_zero_yields_copy():
    src = [1, 2]
    out = split(src, maxsplit=0)
    assert out == [[1, 2]] and out[0] is not src
