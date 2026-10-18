from datetime import date

from boltons.timeutils import daterange


def test_year_step():
    r = list(daterange(date(2015, 1, 1), date(2018, 1, 1), step=(1, 0, 0)))
    assert r == [date(2015, 1, 1), date(2016, 1, 1), date(2017, 1, 1)]


def test_year_step_inclusive():
    r = list(daterange(date(2015, 1, 1), date(2017, 1, 1), step=(1, 0, 0),
                       inclusive=True))
    assert r[-1] == date(2017, 1, 1) and len(r) == 3


def test_month_step_through_december():
    r = list(daterange(date(2015, 10, 1), date(2016, 3, 1), step=(0, 1, 0)))
    assert r == [date(2015, 10, 1), date(2015, 11, 1), date(2015, 12, 1),
                 date(2016, 1, 1), date(2016, 2, 1)]


def test_month_step_from_december():
    r = list(daterange(date(2015, 12, 1), date(2016, 3, 1), step=(0, 1, 0)))
    assert r == [date(2015, 12, 1), date(2016, 1, 1), date(2016, 2, 1)]


def test_large_month_step():
    r = list(daterange(date(2015, 12, 1), date(2017, 1, 1), step=(0, 13, 0)))
    assert r == [date(2015, 12, 1), date(2017, 1, 1)][:1]
    r = list(daterange(date(2015, 12, 1), date(2017, 2, 1), step=(0, 13, 0)))
    assert r == [date(2015, 12, 1), date(2017, 1, 1)]


def test_year_and_month_step_combined():
    r = list(daterange(date(2015, 11, 1), date(2018, 1, 1), step=(1, 2, 0)))
    assert r == [date(2015, 11, 1), date(2017, 1, 1)]


def test_year_step_with_day_step():
    r = list(daterange(date(2015, 1, 1), date(2018, 1, 1), step=(1, 0, 1)))
    assert r == [date(2015, 1, 1), date(2016, 1, 2), date(2017, 1, 3)]
