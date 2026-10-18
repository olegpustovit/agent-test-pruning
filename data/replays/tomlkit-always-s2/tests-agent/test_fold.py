from datetime import datetime
from datetime import time

from tomlkit.items import DateTime
from tomlkit.items import Time
from tomlkit.items import item


def test_item_datetime_preserves_fold():
    dt = item(datetime(2020, 1, 1, 1, 30, fold=1))
    assert isinstance(dt, DateTime)
    assert dt.fold == 1
    assert item(datetime(2020, 1, 1, 1, 30)).fold == 0


def test_item_time_preserves_fold():
    t = item(time(1, 30, fold=1))
    assert isinstance(t, Time)
    assert t.fold == 1
    assert item(time(1, 30)).fold == 0


def test_datetime_constructor_fold():
    dt = DateTime(2020, 1, 1, 1, 30, 0, 0, None, fold=1)
    assert dt.fold == 1
    assert DateTime(2020, 1, 1, 1, 30, 0, 0, None).fold == 0


def test_time_constructor_fold():
    assert Time(1, 30, 0, 0, None, fold=1).fold == 1
    assert Time(1, 30, 0, 0, None).fold == 0


def test_datetime_arithmetic_keeps_fold():
    dt = item(datetime(2020, 1, 1, 1, 30, fold=1))
    assert isinstance(dt + __import__("datetime").timedelta(minutes=1), DateTime)
    assert (dt.replace(minute=45)).fold == 1


def test_time_replace_keeps_fold():
    t = item(time(1, 30, fold=1))
    assert t.replace(minute=45).fold == 1
