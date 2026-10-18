import boltons.strutils as strutils


def test_all_names_exist():
    for name in strutils.__all__:
        assert hasattr(strutils, name), name


def test_all_has_renamed_functions():
    assert 'complement_int_list' in strutils.__all__
    assert 'int_ranges_from_int_list' in strutils.__all__
    assert 'int_list_complement' not in strutils.__all__
    assert 'int_list_to_int_tuples' not in strutils.__all__


def test_star_import():
    ns = {}
    exec('from boltons.strutils import *', ns)
    assert callable(ns['complement_int_list'])
    assert callable(ns['int_ranges_from_int_list'])
