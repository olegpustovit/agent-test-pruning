from datetime import time
from datetime import timedelta
from datetime import timezone

import pytest

from tomlkit import dumps
from tomlkit import item
from tomlkit import parse


TZ = timezone(timedelta(hours=2))


@pytest.mark.parametrize(
    "value, expected",
    [
        (time(7, 32, 0, tzinfo=TZ), "07:32:00"),
        (time(7, 32, 0, 500000, tzinfo=TZ), "07:32:00.5"),
        (time(7, 32, 1, 123456, tzinfo=timezone.utc), "07:32:01.123456"),
        (time(7, 32, 0), "07:32:00"),
        (time(7, 32, 0, 120), "07:32:00.00012"),
    ],
)
def test_item_time_render(value, expected):
    assert item(value).as_string() == expected


def test_tz_aware_time_roundtrip():
    doc = {"t": time(7, 32, tzinfo=TZ)}
    out = dumps(doc)
    assert out == "t = 07:32:00\n"
    assert parse(out)["t"] == time(7, 32)


def test_time_replace_has_no_offset():
    t = item(time(7, 32, tzinfo=TZ))
    r = t.replace(hour=8)
    assert r.as_string() == "08:32:00"
    assert r.tzinfo == TZ
