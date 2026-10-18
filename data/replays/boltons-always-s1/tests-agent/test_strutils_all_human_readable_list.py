import boltons.strutils
from boltons import strutils


def test_in_all():
    assert 'human_readable_list' in strutils.__all__


def test_all_names_exist():
    for name in strutils.__all__:
        assert hasattr(strutils, name)


def test_wildcard_import():
    ns = {}
    exec('from boltons.strutils import *', ns)
    assert ns['human_readable_list'] is strutils.human_readable_list
    assert ns['human_readable_list'](['a', 'b', 'c']) == 'a, b, and c'


def test_dir():
    assert 'human_readable_list' in dir(boltons.strutils)
