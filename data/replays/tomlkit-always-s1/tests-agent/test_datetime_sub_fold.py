from datetime import datetime
from datetime import timedelta
from datetime import timezone

import pytest

from tomlkit.items import DateTime


zoneinfo = pytest.importorskip("zoneinfo")


def _ny():
    try:
        return zoneinfo.ZoneInfo("America/New_York")
    except Exception:
        pytest.skip("tzdata unavailable")


@pytest.mark.parametrize("fold", [0, 1])
def test_sub_datetime_preserves_fold(fold):
    tz = _ny()
    # 2021-11-07 01:30 is ambiguous in New York
    kwargs = dict(tzinfo=tz, fold=fold)
    plain = datetime(2021, 11, 7, 1, 30, **kwargs)
    item = DateTime(2021, 11, 7, 1, 30, 0, 0, tz, fold=fold)
    other = datetime(2021, 11, 7, 0, 0, tzinfo=timezone.utc)

    assert item.fold == fold
    assert item - other == plain - other


def test_sub_folds_differ_by_one_hour():
    tz = _ny()
    other = datetime(2021, 11, 7, 0, 0, tzinfo=timezone.utc)
    first = DateTime(2021, 11, 7, 1, 30, 0, 0, tz, fold=0)
    second = DateTime(2021, 11, 7, 1, 30, 0, 0, tz, fold=1)
    assert second - other - (first - other) == timedelta(hours=1)


def test_sub_timedelta_returns_datetime_item():
    tz = _ny()
    item = DateTime(2021, 11, 7, 1, 30, 0, 0, tz, fold=1)
    result = item - timedelta(minutes=10)
    assert isinstance(result, DateTime)
    assert result.minute == 20
