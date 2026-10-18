from datetime import date, datetime

from boltons.timeutils import daterange


def test_equal_start_stop_exclusive_is_empty():
    d = date(2020, 1, 1)
    assert list(daterange(d, d)) == []


def test_equal_start_stop_inclusive_yields_once():
    d = date(2020, 1, 1)
    assert list(daterange(d, d, inclusive=True)) == [d]


def test_equal_start_stop_month_step_terminates():
    d = date(2020, 1, 15)
    assert list(daterange(d, d, step=(0, 1, 0))) == []
    assert list(daterange(d, d, step=(0, 1, 0), inclusive=True)) == [d]


def test_equal_datetimes():
    d = datetime(2020, 1, 1, 12)
    assert list(daterange(d, d)) == []
    assert list(daterange(d, d, inclusive=True)) == [d]
