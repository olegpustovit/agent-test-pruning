import pytest

from boltons import funcutils, iterutils, namedutils, strutils, debugutils


def test_get_path_bytes_not_split():
    # bytes is no longer treated as a dotted path string
    with pytest.raises(Exception):
        iterutils.get_path({'a': 1}, b'a')
    assert iterutils.get_path({'a': {'b': 2}}, 'a.b') == 2


def test_bucketize_str_key():
    class O:
        def __init__(self, x):
            self.x = x
    res = iterutils.bucketize([O(1), O(1), O(2)], 'x')
    assert sorted(len(v) for v in res.values()) == [1, 2]


def test_unique_iter_bytes_key_rejected():
    with pytest.raises(TypeError):
        list(iterutils.unique_iter([1, 2], key=b'x'))


def test_namedtuple_str_fields():
    assert namedutils.namedtuple('P', 'a, b')._fields == ('a', 'b')
    assert namedutils.namedlist('L', 'a b')(1, 2).a == 1


def test_get_module_callables_str():
    a, b = funcutils.get_module_callables('boltons.funcutils')
    assert 'wraps' in a or 'wraps' in b


def test_parse_wraps_expected_str():
    assert funcutils._parse_wraps_expected('a') == [('a', funcutils.NO_DEFAULT)]
    with pytest.raises(ValueError):
        funcutils._parse_wraps_expected([b'a'])


def test_multireplace_str():
    assert strutils.MultiReplace([('a', 'b')]).sub('aa') == 'bb'


def test_wrap_trace_str_which_and_events():
    class C:
        x = 0
        y = 0

    out = []

    def hook(event, label, obj, attr_name, args, kwargs, **kw):
        out.append((event, attr_name))

    obj = debugutils.wrap_trace(C(), hook=hook, which='__setattr__', events='set')
    obj.x = 1
    obj.y = 2
    assert out == [('set', 'x'), ('set', 'y')]
