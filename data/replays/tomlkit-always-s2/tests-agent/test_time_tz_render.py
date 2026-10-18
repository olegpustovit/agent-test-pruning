from datetime import time, timedelta, timezone

import tomlkit

from tomlkit import item


TZ = timezone(timedelta(hours=2))


def test_item_tz_aware_time_has_no_offset():
    t = item(time(7, 32, 0, tzinfo=TZ))
    assert t.as_string() == "07:32:00"
    assert t.tzinfo == TZ


def test_item_tz_aware_time_with_microseconds():
    assert item(time(7, 32, 1, 500000, tzinfo=TZ)).as_string() == "07:32:01.5"
    assert item(time(7, 32, 1, 123456, tzinfo=timezone.utc)).as_string() == "07:32:01.123456"


def test_item_naive_time_unchanged():
    assert item(time(7, 32, 0)).as_string() == "07:32:00"
    assert item(time(7, 32, 0, 1)).as_string() == "07:32:00.000001"


def test_document_roundtrip_with_tz_aware_time():
    doc = tomlkit.document()
    doc["t"] = time(7, 32, 0, tzinfo=TZ)
    out = tomlkit.dumps(doc)
    assert out == "t = 07:32:00\n"
    assert tomlkit.parse(out)["t"] == time(7, 32, 0)


def test_time_replace_renders_without_offset():
    t = item(time(7, 32, 0))
    r = t.replace(hour=8, tzinfo=TZ)
    assert r.as_string() == "08:32:00"
    r = t.replace(microsecond=250000)
    assert r.as_string() == "07:32:00.25"
