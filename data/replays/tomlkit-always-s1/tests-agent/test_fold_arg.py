from datetime import datetime, time, timedelta

from tomlkit.items import DateTime, Time, item


def test_item_preserves_datetime_fold():
    v = item(datetime(2020, 1, 1, 1, 30, fold=1))
    assert isinstance(v, DateTime)
    assert v.fold == 1


def test_item_preserves_time_fold():
    v = item(time(1, 30, fold=1))
    assert isinstance(v, Time)
    assert v.fold == 1


def test_constructors_default_fold_zero():
    assert DateTime(2020, 1, 1, 0, 0, 0, 0, None).fold == 0
    assert Time(1, 2, 3, 0, None).fold == 0


def test_constructors_accept_fold():
    assert DateTime(2020, 1, 1, 0, 0, 0, 0, None, fold=1).fold == 1
    assert Time(1, 2, 3, 0, None, fold=1).fold == 1


def test_replace_keeps_fold():
    dt = item(datetime(2020, 1, 1, 1, 30, fold=1))
    assert dt.replace(minute=5).fold == 1
    t = item(time(1, 30, fold=1))
    assert t.replace(minute=5).fold == 1


def test_arithmetic_fold():
    dt = DateTime(2020, 1, 1, 1, 30, 0, 0, None, fold=1)
    assert (dt + timedelta(hours=1)).hour == 2
