from datetime import time
from datetime import timedelta
from datetime import timezone

import tomlkit

from tomlkit import item


TZ = timezone(timedelta(hours=2))


def test_item_tz_aware_time_has_no_offset():
    t = item(time(7, 32, 0, tzinfo=TZ))
    assert t.as_string() == "07:32:00"


def test_item_tz_aware_time_with_microseconds():
    t = item(time(7, 32, 1, 500000, tzinfo=TZ))
    assert t.as_string() == "07:32:01.5"


def test_naive_time_unchanged():
    assert item(time(7, 32)).as_string() == "07:32:00"
    assert item(time(7, 32, 0, 123456)).as_string() == "07:32:00.123456"


def test_tz_aware_time_roundtrips_in_document():
    doc = tomlkit.document()
    doc["t"] = time(7, 32, 0, tzinfo=TZ)
    text = tomlkit.dumps(doc)
    assert text == "t = 07:32:00\n"
    assert tomlkit.parse(text)["t"] == time(7, 32)


def test_replace_keeps_valid_raw():
    t = item(time(7, 32, 0))
    r = t.replace(tzinfo=TZ)
    assert r.as_string() == "07:32:00"
    r = t.replace(microsecond=250000)
    assert r.as_string() == "07:32:00.25"
    assert tomlkit.parse(f"t = {r.as_string()}")["t"] == time(7, 32, 0, 250000)
