from boltons.statsutils import Stats


def test_bin_bounds_zero_iqr():
    s = Stats([1, 5, 5, 5, 5, 5, 9])
    assert s._get_bin_bounds() == [1.0]
    assert s._get_bin_bounds(with_max=True) == [1.0, 9.0]


def test_histogram_counts_zero_iqr():
    s = Stats([1, 5, 5, 5, 5, 5, 9])
    counts = s.get_histogram_counts()
    assert counts == [(1.0, 7)]


def test_format_histogram_zero_iqr():
    s = Stats([1, 5, 5, 5, 5, 5, 9])
    assert isinstance(s.format_histogram(), str)


def test_all_equal_data():
    s = Stats([3, 3, 3, 3, 3])
    assert s._get_bin_bounds() == [3.0]
    assert s._get_bin_bounds(with_max=True) == [3.0, 3.0]


def test_nonzero_iqr_unchanged():
    s = Stats(list(range(100)))
    bounds = s._get_bin_bounds()
    assert len(bounds) > 1
    assert bounds[0] == 0
