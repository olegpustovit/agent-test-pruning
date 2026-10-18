import subprocess
import sys
import warnings
from datetime import datetime, timedelta, timezone

from boltons import timeutils
from boltons.timeutils import dt_to_timestamp, UTC


def test_epoch_naive_removed():
    assert not hasattr(timeutils, 'EPOCH_NAIVE')
    assert timeutils.EPOCH_AWARE == datetime(1970, 1, 1, tzinfo=timezone.utc)


def test_naive_epoch_and_values():
    assert dt_to_timestamp(datetime(1970, 1, 1)) == 0.0
    assert dt_to_timestamp(datetime(1970, 1, 2, 0, 0, 1, 500000)) == 86401.5
    assert dt_to_timestamp(datetime(1969, 12, 31)) == -86400.0


def test_aware_matches_naive_utc():
    naive = datetime(2020, 5, 17, 12, 30, 45)
    assert dt_to_timestamp(naive) == dt_to_timestamp(naive.replace(tzinfo=UTC))
    assert dt_to_timestamp(naive) == 1589718645.0


def test_aware_non_utc():
    tz = timezone(timedelta(hours=2))
    assert dt_to_timestamp(datetime(1970, 1, 1, 2, tzinfo=tz)) == 0.0


def test_import_no_deprecation_warning():
    code = ("import warnings; warnings.simplefilter('error'); "
            "import boltons.timeutils")
    r = subprocess.run([sys.executable, '-c', code],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
