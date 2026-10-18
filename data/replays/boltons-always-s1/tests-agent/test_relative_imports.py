import importlib

import pytest

from boltons import typeutils, listutils, dictutils

SENTINELS = [
    ('cacheutils', ['_MISSING', '_KWARG_MARK']),
    ('debugutils', ['_UNSET']),
    ('dictutils', ['_MISSING']),
    ('funcutils', ['NO_DEFAULT']),
    ('iterutils', ['_UNSET', '_REMAP_EXIT']),
    ('listutils', ['_MISSING']),
    ('queueutils', ['_REMOVED']),
    ('setutils', ['_MISSING']),
    ('socketutils', ['_UNSET']),
    ('tableutils', ['_MISSING']),
    ('urlutils', ['_MISSING']),
]


@pytest.mark.parametrize('modname,names', SENTINELS)
def test_sentinels_come_from_typeutils(modname, names):
    mod = importlib.import_module('boltons.' + modname)
    for name in names:
        val = getattr(mod, name)
        # make_sentinel instances have a custom class, not plain object
        assert type(val) is not object, (modname, name)
        assert type(val).__module__ != 'builtins'
        assert not bool(val)


def test_sentinel_is_falsy_and_distinct():
    from boltons import setutils
    assert setutils._MISSING is not dictutils._MISSING


def test_queueutils_uses_barrel_list():
    from boltons import queueutils
    assert queueutils.BList is listutils.BarrelList


def test_urlutils_omd_is_dictutils_omd():
    from boltons import urlutils
    assert urlutils.OrderedMultiDict is dictutils.OrderedMultiDict
