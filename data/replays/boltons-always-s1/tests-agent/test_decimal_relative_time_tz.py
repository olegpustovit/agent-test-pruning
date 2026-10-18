from datetime import datetime, timedelta, timezone

import pytest

from boltons.timeutils import decimal_relative_time


def test_aware_default_other_matches_tz():
    tz = timezone(timedelta(hours=5))
    d = datetime.now(tz) - timedelta(hours=2)
    assert decimal_relative_time(d, ndigits=1) == (2.0, 'hours')


def test_aware_utc_future():
    d = datetime.now(timezone.utc) + timedelta(days=3)
    delta, unit = decimal_relative_time(d, ndigits=1)
    assert unit == 'days'
    assert round(delta) == -3


def test_naive_default_other_still_works():
    d = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(minutes=30)
    assert decimal_relative_time(d) == (30, 'minutes')
