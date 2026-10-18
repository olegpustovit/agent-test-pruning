import pytest

from boltons.cacheutils import CachedMethod, ThresholdCounter


def test_cachedmethod_str_cache_uses_attribute():

    class B:
        def __init__(self):
            self.c = {}
            self.calls = 0

        def f(self, x):
            self.calls += 1
            return x * 2
        f = CachedMethod(f, 'c')

    b = B()
    assert b.f(2) == 4
    assert b.f(2) == 4
    assert b.calls == 1
    assert len(b.c) == 1


def test_cachedmethod_bytes_cache_not_attribute_name():
    # bytes is no longer treated as an attribute name
    with pytest.raises(TypeError):
        CachedMethod(lambda self: 1, b'c')


def test_most_common_zero_and_negative():
    tc = ThresholdCounter()
    tc.update('aabbbc')
    assert tc.most_common(0) == []
    assert tc.most_common(-1) == []


def test_most_common_positive():
    tc = ThresholdCounter()
    tc.update('aabbbc')
    assert tc.most_common(1) == [('b', 3)]
    assert tc.most_common(10)[0] == ('b', 3)
    assert len(tc.most_common(10)) == 3
