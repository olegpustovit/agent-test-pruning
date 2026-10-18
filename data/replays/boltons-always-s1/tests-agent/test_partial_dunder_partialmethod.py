import functools

import pytest

from boltons.funcutils import CachedInstancePartial, InstancePartial


def _f(self, a, b=0):
    return (a, b)


@pytest.mark.parametrize('cls', [InstancePartial, CachedInstancePartial])
def test_dunder_partialmethod(cls):
    p = cls(_f, 1, b=2)
    pm = p.__partialmethod__
    assert isinstance(pm, functools.partialmethod)
    assert pm.func is _f
    assert pm.args == (1,)
    assert pm.keywords == {'b': 2}


@pytest.mark.parametrize('cls', [InstancePartial, CachedInstancePartial])
def test_private_alias_delegates_to_dunder(cls):
    p = cls(_f, 1, b=2)
    pm = p._partialmethod
    assert isinstance(pm, functools.partialmethod)
    assert (pm.func, pm.args, pm.keywords) == (_f, (1,), {'b': 2})


@pytest.mark.parametrize('cls', [InstancePartial, CachedInstancePartial])
def test_delegation_through_dunder(cls, monkeypatch):
    sentinel = object()
    monkeypatch.setattr(cls, '__partialmethod__', property(lambda self: sentinel))
    assert cls(_f)._partialmethod is sentinel


@pytest.mark.parametrize('cls', [InstancePartial, CachedInstancePartial])
def test_method_binding(cls):
    class C:
        m = cls(_f, b=6)

    assert C().m(1) == (1, 6)
