import copy
import pickle

import pytest

from boltons.dictutils import OrderedMultiDict as OMD


class Sub(OMD):
    pass


def _make():
    omd = OMD()
    omd.add('a', 1)
    omd.add('b', 2)
    omd.add('a', 3)
    omd.add('a', 4)
    return omd


def _check(new, orig):
    assert new == orig
    assert new is not orig
    assert new.getlist('a') == [1, 3, 4]
    assert new.getlist('b') == [2]
    assert list(new.iteritems(multi=True)) == list(orig.iteritems(multi=True))


def test_copy():
    _check(copy.copy(_make()), _make())


def test_deepcopy():
    _check(copy.deepcopy(_make()), _make())


@pytest.mark.parametrize('proto', range(0, pickle.HIGHEST_PROTOCOL + 1))
def test_pickle_protocols(proto):
    omd = _make()
    _check(pickle.loads(pickle.dumps(omd, proto)), omd)


def test_copy_independent():
    omd = _make()
    new = copy.deepcopy(omd)
    new.add('a', 99)
    assert omd.getlist('a') == [1, 3, 4]
    assert new.getlist('a') == [1, 3, 4, 99]


def test_deepcopy_values_copied():
    omd = OMD()
    omd.add('k', [1])
    omd.add('k', [2])
    new = copy.deepcopy(omd)
    assert new.getlist('k') == [[1], [2]]
    assert new.getlist('k')[0] is not omd.getlist('k')[0]


def test_empty_and_subclass():
    assert copy.deepcopy(OMD()) == OMD()

    s = Sub(); s.add('x', 1); s.add('x', 2)
    for c in (copy.copy(s), copy.deepcopy(s), pickle.loads(pickle.dumps(s))):
        assert type(c) is Sub
        assert c.getlist('x') == [1, 2]
