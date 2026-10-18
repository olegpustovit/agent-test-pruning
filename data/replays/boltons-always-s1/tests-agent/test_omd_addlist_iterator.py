import pytest

from boltons import dictutils, urlutils

CLASSES = [dictutils.OrderedMultiDict, urlutils.OrderedMultiDict]


@pytest.mark.parametrize("cls", CLASSES)
def test_addlist_generator(cls):
    omd = cls()
    omd.addlist('a', (i for i in range(3)))
    assert omd.getlist('a') == [0, 1, 2]
    assert omd.get('a') == 2
    assert list(omd.keys()) == ['a']
    assert list(omd.items(multi=True)) == [('a', 0), ('a', 1), ('a', 2)]


@pytest.mark.parametrize("cls", CLASSES)
def test_addlist_empty_iterator(cls):
    omd = cls()
    omd.addlist('a', iter([]))
    assert 'a' not in omd
    assert len(omd) == 0
    assert list(omd.keys()) == []


@pytest.mark.parametrize("cls", CLASSES)
def test_addlist_existing_key_iterator(cls):
    omd = cls([('a', 1)])
    omd.addlist('a', iter([2, 3]))
    assert omd.getlist('a') == [1, 2, 3]


@pytest.mark.parametrize("cls", CLASSES)
def test_addlist_sequence_still_works(cls):
    omd = cls()
    omd.addlist('a', [1, 2])
    omd.addlist('b', (3,))
    assert omd.getlist('a') == [1, 2]
    assert omd.getlist('b') == [3]
