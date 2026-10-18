import copy
import pickle

import pytest

from boltons.dictutils import OrderedMultiDict, OMD


class SubOMD(OrderedMultiDict):
    pass


def _sample():
    omd = OrderedMultiDict()
    omd.add('a', 1)
    omd.add('b', 2)
    omd.add('a', 3)
    omd.add('c', 4)
    return omd


@pytest.mark.parametrize('proto', range(pickle.HIGHEST_PROTOCOL + 1))
def test_pickle_roundtrip(proto):
    omd = _sample()
    out = pickle.loads(pickle.dumps(omd, proto))
    assert type(out) is OrderedMultiDict
    assert list(out.iteritems(multi=True)) == list(omd.iteritems(multi=True))
    assert out == omd
    assert out.getlist('a') == [1, 3]
    assert out['a'] == 3


def test_pickle_empty():
    out = pickle.loads(pickle.dumps(OrderedMultiDict()))
    assert len(out) == 0
    assert list(out.iteritems(multi=True)) == []


def test_pickled_is_usable_and_independent():
    omd = _sample()
    out = pickle.loads(pickle.dumps(omd))
    out.add('d', 5)
    out.add('a', 6)
    assert out.getlist('a') == [1, 3, 6]
    assert 'd' not in omd
    assert omd.getlist('a') == [1, 3]
    out.pop('b')
    assert 'b' in omd


def test_pickle_subclass():
    omd = SubOMD([('x', 1), ('x', 2)])
    out = pickle.loads(pickle.dumps(omd))
    assert type(out) is SubOMD
    assert out.getlist('x') == [1, 2]


def test_copy_method():
    omd = _sample()
    out = omd.copy()
    assert out == omd
    out.add('z', 9)
    assert 'z' not in omd


def test_new_initializes_linked_list():
    omd = OrderedMultiDict.__new__(OrderedMultiDict)
    assert len(omd) == 0
    omd.add('k', 1)
    assert omd.getlist('k') == [1]


def test_omd_alias_pickles():
    omd = OMD([(1, 2), (1, 3)])
    assert pickle.loads(pickle.dumps(omd)).getlist(1) == [2, 3]
