from datetime import datetime
from datetime import time
from datetime import timezone

from tomlkit import item
from tomlkit.items import DateTime
from tomlkit.items import Time
from tomlkit.items import Trivia


def test_item_preserves_fold():
    assert item(datetime(2020, 1, 1, 1, 30, fold=1)).fold == 1
    assert item(time(1, 30, fold=1)).fold == 1
    assert item(datetime(2020, 1, 1, tzinfo=timezone.utc, fold=1)).fold == 1


def test_constructors_fold():
    assert Time(1, 2, 3, 0, None, Trivia(), "", fold=1).fold == 1
    assert Time(1, 2, 3, 0, None).fold == 0
    assert DateTime(2020, 1, 1, 1, 2, 3, 0, None, fold=1).fold == 1


def test_replace_keeps_fold():
    dt = item(datetime(2020, 1, 1, 1, 30, fold=1))
    assert isinstance(dt, DateTime)
    assert dt.replace(minute=5).fold == 1
    t = item(time(1, 30, fold=1))
    assert isinstance(t, Time)
    assert t.replace(minute=5).fold == 1


def test_sub_keeps_fold():
    from datetime import timedelta
    from zoneinfo import ZoneInfo

    tz = ZoneInfo("America/New_York")
    base = datetime(2020, 11, 1, 0, 0, tzinfo=timezone.utc)
    first = item(datetime(2020, 11, 1, 1, 30, tzinfo=tz, fold=0))
    second = item(datetime(2020, 11, 1, 1, 30, tzinfo=tz, fold=1))
    assert first - base == timedelta(hours=5, minutes=30)
    assert second - base == timedelta(hours=6, minutes=30)


def test_unwrap_keeps_fold():
    dt = item(datetime(2020, 1, 1, 1, 30, fold=1)).unwrap()
    assert type(dt) is datetime
    assert dt.fold == 1
    t = item(time(1, 30, fold=1)).unwrap()
    assert type(t) is time
    assert t.fold == 1
    assert item(datetime(2020, 1, 1, 1, 30)).unwrap().fold == 0
    assert item(time(1, 30)).unwrap().fold == 0
