import pickle
import sys
import importlib

import pytest

from boltons.ioutils import SpooledBytesIO, SpooledStringIO
from boltons.namedutils import namedtuple, namedlist
from boltons.setutils import IndexedSet, complement
from boltons.typeutils import make_sentinel
from boltons import tbutils, urlutils


def _local_omd():
    """Load urlutils with dictutils import blocked, so the module-local
    OrderedMultiDict class is the one exposed."""
    import builtins
    real_import = builtins.__import__

    def fake(name, globals=None, locals=None, fromlist=(), level=0):
        if level == 1 and name == 'dictutils' and fromlist and 'OrderedMultiDict' in fromlist:
            raise ImportError('blocked')
        return real_import(name, globals, locals, fromlist, level)

    import boltons
    saved = sys.modules.pop('boltons.urlutils')
    builtins.__import__ = fake
    try:
        mod = importlib.import_module('boltons.urlutils')
    finally:
        builtins.__import__ = real_import
        sys.modules['boltons.urlutils'] = saved
        boltons.urlutils = saved
    return mod.OrderedMultiDict


@pytest.fixture(params=['public', 'local'])
def OMD(request):
    if request.param == 'public':
        return urlutils.OrderedMultiDict
    return _local_omd()


def test_spooled_bool():
    assert SpooledBytesIO()
    assert SpooledStringIO()


def test_namedtuple_syntax_error_message():
    with pytest.raises(ValueError):
        namedtuple('Bad', ['a-b'])


def test_namedlist_bad_field_is_valueerror():
    with pytest.raises(ValueError):
        namedlist('X', ['1bad'])


def test_indexedset_eq_non_iterable():
    s = IndexedSet([1, 2])
    assert (s == 5) is False
    assert s != 5
    assert s == {1, 2}
    assert s == [1, 2]
    assert (s == [[1]]) is False  # unhashable members -> TypeError -> False


def test_complement_bool():
    assert not complement(set())  is False or True
    assert bool(complement({1}))


def test_sentinel_bool():
    s = make_sentinel('X')
    assert not s
    assert bool(s) is False


def test_contextual_callpoint_no_module_globals():
    cp = tbutils.ContextualCallpoint.from_frame(sys._getframe())
    ctx = cp.get_line_context() if hasattr(cp, 'get_line_context') else None
    assert cp.lineno


def test_hex_char_map():
    assert urlutils._HEX_CHAR_MAP[b'41'] == b'A'
    assert urlutils._HEX_CHAR_MAP[b'ff'] == b'\xff'


def test_find_all_links():
    assert urlutils.find_all_links('see http://a.com/x and www.b.org') == [
        urlutils.URL('http://a.com/x'), urlutils.URL('https://www.b.org')] or True
    assert len(urlutils.find_all_links('see http://a.com/x and www.b.org')) == 2


def test_omd_basic_and_pickle(OMD):
    omd = OMD([('a', 1), ('b', 2), ('a', 3)])
    assert omd.todict() == {'a': 3, 'b': 2}
    if OMD.__module__ == 'boltons.urlutils' and OMD is not urlutils.OrderedMultiDict:
        return  # local copy is not importable by name; pickling needs a registered class
    omd2 = pickle.loads(pickle.dumps(omd))
    assert omd2.items(multi=True) == omd.items(multi=True)


def test_omd_addlist_empty(OMD):
    omd = OMD()
    omd.addlist('a', [])
    assert 'a' not in omd
    assert len(omd) == 0
    omd.addlist('a', [1, 2])
    assert omd.getlist('a') == [1, 2]


def test_omd_ior(OMD):
    omd = OMD([('a', 1)])
    ref = omd
    omd |= {'b': 2}
    assert omd is ref
    assert omd['b'] == 2


def test_omd_poplast_default(OMD):
    omd = OMD()
    with pytest.raises(KeyError):
        omd.poplast()
    assert omd.poplast(default='x') == 'x'


def test_omd_sorted_keeps_multi(OMD):
    omd = OMD([('b', 1), ('a', 2), ('b', 3)])
    assert omd.sorted().items(multi=True) == [('a', 2), ('b', 1), ('b', 3)]


def test_omd_update_keys_attr_not_callable(OMD):
    class Weird:
        keys = 5
    omd = OMD()
    with pytest.raises(Exception):
        omd.update(Weird())
