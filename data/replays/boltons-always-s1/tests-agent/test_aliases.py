import functools
from datetime import timedelta
from types import MethodType, ModuleType

import pytest

from boltons import deprutils, funcutils, timeutils, urlutils
from boltons.mathutils import Bits
from boltons.funcutils import InstancePartial, CachedInstancePartial


def test_total_seconds():
    td = timedelta(days=1, seconds=5, microseconds=500000)
    assert timeutils.total_seconds(td) == td.total_seconds() == 86405.5


def test_total_ordering_reexport():
    assert funcutils.total_ordering is functools.total_ordering


def test_deprutils_moduletype():
    assert deprutils.ModuleType is ModuleType


def test_instance_partial():
    class A:
        def f(self, x, y):
            return (self, x, y)
        g = InstancePartial(f, 1)
    a = A()
    assert isinstance(a.g, MethodType)
    assert a.g(2) == (1, a, 2)


def test_cached_instance_partial():
    class A:
        def f(self, x, y):
            return (self, x, y)
        g = CachedInstancePartial(f, 1)
    a = A()
    assert a.g(2) == (1, a, 2)
    assert a.g is a.g


def test_bits_inputs():
    assert Bits(5).as_bin() == Bits('101').as_bin()
    assert Bits('0x0f').as_int() == 15
    assert Bits(b'0b101').as_int() == 5
    assert Bits([1, 0, 1]).as_int() == 5
    assert Bits('0b101').as_int() == 5
    with pytest.raises(TypeError):
        Bits(1.5)
    with pytest.raises(ValueError):
        Bits(-1)


def test_urlutils_str_paths():
    assert urlutils.to_unicode(5) == '5'
    assert urlutils.unquote_to_bytes('a%20b') == b'a b'
    assert urlutils.unquote_to_bytes(b'a%20b') == b'a b'
    u = urlutils.URL('http://example.com:8080/p?q=1')
    assert u.to_text() == 'http://example.com:8080/p?q=1'
    assert urlutils.URL('http://example.com:80/').to_text() == 'http://example.com/'
    assert urlutils.parse_url('http://a.com:81/x')['port'] == 81
    links = urlutils.find_all_links('hi http://a.com/x there', with_text=True)
    assert links[0] == 'hi ' and links[2] == ' there'
