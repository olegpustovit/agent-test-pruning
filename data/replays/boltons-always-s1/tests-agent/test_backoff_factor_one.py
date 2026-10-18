import pytest

from boltons.iterutils import backoff, backoff_iter


def test_factor_one_equal_start_stop_single_value():
    assert list(backoff_iter(5, 5, factor=1.0)) == [5.0]
    assert backoff(5, 5, factor=1) == [5.0]


def test_factor_one_start_less_than_stop_raises():
    with pytest.raises(ValueError):
        list(backoff_iter(1, 10, factor=1.0))
    with pytest.raises(ValueError):
        backoff(0, 10, factor=1.0)


def test_factor_one_with_explicit_count_unchanged():
    assert backoff(2, 2, count=3, factor=1.0) == [2.0, 2.0, 2.0]
    assert backoff(1, 10, count=3, factor=1.0) == [1.0, 1.0, 1.0]


def test_factor_above_one_inferred_count_unchanged():
    assert backoff(1, 16) == [1.0, 2.0, 4.0, 8.0, 16.0]
    assert backoff(0, 4) == [0.0, 1.0, 2.0, 4.0]
