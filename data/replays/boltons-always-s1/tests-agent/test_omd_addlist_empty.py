import pytest
from boltons.dictutils import OrderedMultiDict as OMD


def test_addlist_empty_list_does_not_create_key():
    omd = OMD()
    omd.addlist('a', [])
    assert 'a' not in omd
    assert len(omd) == 0
    assert omd.keys() == []
    assert omd.todict() == {}


def test_addlist_empty_tuple_and_existing_key():
    omd = OMD([('a', 1)])
    omd.addlist('a', ())
    omd.addlist('b', ())
    assert omd.items() == [('a', 1)]
    assert 'b' not in omd


def test_addlist_nonempty_still_works():
    omd = OMD()
    omd.addlist('a', [1, 2])
    assert omd.getlist('a') == [1, 2]


def test_poplast_empty_default():
    omd = OMD()
    assert omd.poplast(default=5) == 5
    assert omd.poplast(default=None) is None


def test_poplast_empty_no_default_raises():
    with pytest.raises(KeyError):
        OMD().poplast()


def test_poplast_nonempty_ignores_default():
    omd = OMD([('a', 1), ('b', 2)])
    assert omd.poplast(default=9) == 2
