from datetime import datetime
from datetime import timezone
from zoneinfo import ZoneInfo

import pytest

from tomlkit.items import DateTime


NY = ZoneInfo("America/New_York")


@pytest.mark.parametrize("fold,offset_hours", [(0, 4), (1, 5)])
def test_datetime_sub_datetime_respects_fold(fold, offset_hours):
    # 2021-11-07 01:30 in New York is ambiguous: fold=0 is EDT, fold=1 is EST.
    a = DateTime(2021, 11, 7, 1, 30, 0, 0, NY, fold=fold)
    b = datetime(2021, 11, 7, 0, 0, tzinfo=timezone.utc)
    expected = datetime(2021, 11, 7, 1, 30, tzinfo=NY, fold=fold) - b
    assert a - b == expected
    # UTC time of a is 01:30 + offset
    assert (a - b).total_seconds() == (1.5 + offset_hours) * 3600
