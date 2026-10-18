import functools

from boltons.funcutils import CachedInstancePartial, InstancePartial


def _f(self, a, b=0):
    return (a, b)


def test_cached_dunder_partialmethod_matches_private():
    p = CachedInstancePartial(_f, 1, b=2)
    pm = p.__partialmethod__
    assert isinstance(pm, functools.partialmethod)
    assert pm.func is _f
    assert pm.args == (1,)
    assert pm.keywords == {'b': 2}
    assert p._partialmethod.args == pm.args


def test_cached_partial_usable_as_method():
    class C:
        m = CachedInstancePartial(_f, b=6)


    c = C()
    assert c.m(1) == (1, 6)
    assert c.m is c.m
    assert isinstance(C.__dict__['m'].__partialmethod__, functools.partialmethod)


def test_instance_partial_private_partialmethod():
    p = InstancePartial(_f, 1)
    assert isinstance(p._partialmethod, functools.partialmethod)
