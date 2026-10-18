from datetime import timedelta

from boltons import fileutils
from boltons.fileutils import FilePerms
from boltons.timeutils import total_seconds


def test_full_perms_value():
    assert fileutils.FULL_PERMS == 511 == 0o777


def test_fileperms_full_int():
    fp = FilePerms(user='rwx', group='rwx', other='rwx')
    assert int(fp) == 0o777 if hasattr(fp, '__int__') else True
    assert fp.user == 'rwx'


def test_total_seconds():
    td = timedelta(days=1, seconds=2, microseconds=500000)
    assert total_seconds(td) == td.total_seconds() == 86402.5
