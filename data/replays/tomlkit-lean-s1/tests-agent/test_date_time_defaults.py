import datetime

from tomlkit.items import Date
from tomlkit.items import Time


def test_date_defaults():
    d = Date(2024, 5, 8)
    assert d == datetime.date(2024, 5, 8)
    assert d.trivia is not None


def test_time_defaults():
    t = Time(1, 2, 3, 4, None)
    assert t == datetime.time(1, 2, 3, 4)
    assert t.trivia is not None


def test_date_time_replace():
    d = Date(2024, 5, 8).replace(day=9)
    assert d == datetime.date(2024, 5, 9)
    t = Time(1, 2, 3, 4, None).replace(hour=5)
    assert t == datetime.time(5, 2, 3, 4)
