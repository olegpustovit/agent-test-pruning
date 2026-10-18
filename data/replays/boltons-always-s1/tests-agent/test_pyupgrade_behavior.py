import io
import pytest

from boltons.cacheutils import LRI, LRU, ThresholdCounter, cachedproperty, cached
from boltons.dictutils import OrderedMultiDict, OneToOne, ManyToMany, FrozenDict
from boltons.excutils import ExceptionCauseMixin
from boltons.fileutils import AtomicSaver
from boltons.formatutils import infer_positional_format_args
from boltons.funcutils import format_invocation, FunctionBuilder, ExistingArgument
from boltons.ioutils import SpooledStringIO, MultiFileReader, is_text_fileobj
from boltons.iterutils import flatten_iter, rstrip_iter, PathAccessError, SequentialGUIDerator
from boltons.listutils import BarrelList
from boltons.mathutils import Bits
from boltons.setutils import IndexedSet, complement
from boltons.socketutils import MessageTooLong, NetstringMessageTooLong
from boltons.statsutils import Stats
from boltons.strutils import (unit_len, a10n, format_int_list, MultiReplace,
                              html2text, asciify)
from boltons.tableutils import Table
from boltons.tbutils import ParsedException
from boltons.timeutils import dt_to_timestamp
from boltons.urlutils import URL


def test_lri_basics_and_repr():
    c = LRI(max_size=2)
    c['a'] = 1
    c['b'] = 2
    c['c'] = 3
    assert 'a' not in c
    assert c.pop('b') == 2
    assert c.popitem() == ('c', 3)
    c['x'] = 1
    assert repr(c).startswith('LRI(max_size=2, on_miss=None, values={')
    c.clear()
    assert len(c) == 0


def test_cached_reprs_and_threshold_counter():
    @cached({})
    def f(x):
        return x
    assert repr(f).startswith('CachedFunction(func=')
    tc = ThresholdCounter(threshold=0.5)
    for ch in 'aabbbc':
        tc.add(ch)
    assert tc['b'] >= 1

    class A:
        @cachedproperty
        def p(self):
            return 1
    assert repr(A.__dict__['p']).startswith('<cachedproperty func=')
    assert A().p == 1


def test_omd():
    omd = OrderedMultiDict([('a', 1), ('a', 2), ('b', 3)])
    assert omd['a'] == 2 and omd.getlist('a') == [1, 2]
    assert omd.todict() == {'a': 2, 'b': 3}
    assert omd.todict(multi=True) == {'a': [1, 2], 'b': [3]}
    assert repr(omd) == "OrderedMultiDict([('a', 1), ('a', 2), ('b', 3)])"
    assert omd.sortedvalues(reverse=True).getlist('a') == [2, 1]
    assert omd.counts()['a'] == 2
    assert omd.popall('a') == [1, 2]
    assert omd.pop('b') == 3


def test_onetoone_manytomany_frozendict():
    with pytest.raises(ValueError) as ei:
        OneToOne.unique({1: 'a', 2: 'a'})
    assert "expected unique values" in str(ei.value) and "'a': [1, 2]" in str(ei.value)
    assert repr(OneToOne({1: 2})) == 'OneToOne({1: 2})'
    assert repr(ManyToMany({1: 2})) == 'ManyToMany([(1, 2)])'
    assert repr(FrozenDict({1: 2})) == 'FrozenDict({1: 2})'


def test_exception_cause_mixin():
    class E(ExceptionCauseMixin):
        pass
    assert str(E('boom')) == 'boom'
    try:
        try:
            raise ValueError('inner')
        except ValueError as ve:
            raise E(ve, 'outer')
    except E as e:
        assert isinstance(e.cause, ValueError)
        assert 'inner' in str(e)


def test_fileutils(tmp_path):
    with pytest.raises(TypeError, match='unexpected kwargs'):
        AtomicSaver(str(tmp_path / 'x'), bogus=1)
    p = tmp_path / 'f.txt'
    with AtomicSaver(str(p)) as f:
        f.write(b'hi')
    assert p.read_bytes() == b'hi'


def test_formatutils_and_funcutils():
    assert infer_positional_format_args('{} and {:>3} {{x}}') == '{0} and {1:>3} {{x}}'
    assert format_invocation('f', (1,), {'b': 'x', 'a': 2}) == "f(1, a=2, b='x')"
    fb = FunctionBuilder.from_func(lambda a, *, k=1: a)
    with pytest.raises(ExistingArgument, match="arg 'a' already in func"):
        fb.add_arg('a')
    with pytest.raises(ExistingArgument, match="kwonly arg list"):
        fb.add_arg('k', 2, kwonly=True)
    with pytest.raises(TypeError, match='expected callable object, not 5'):
        FunctionBuilder.from_func(5)
    fb2 = FunctionBuilder('g', body='return a + k', args=['a'], kwonlyargs=['k'],
                          kwonlydefaults={'k': 1})
    assert fb2.get_func()(1, k=2) == 3


def test_ioutils():
    s = SpooledStringIO()
    s.write('héllo\nworld\n')
    s.seek(0)
    assert s.readlines() == ['héllo\n', 'world\n']
    s.seek(0)
    with pytest.raises(ValueError, match=r'Invalid whence \(5, should be 0, 1, or 2\)'):
        s.seek(0, 5)
    with pytest.raises(OSError):
        s.truncate(-1)
    assert is_text_fileobj(io.StringIO('x')) and not is_text_fileobj(io.BytesIO(b'x'))
    r = MultiFileReader(io.StringIO('ab'), io.StringIO('cd'))
    assert r.read() == 'abcd'
    with pytest.raises(ValueError):
        MultiFileReader(io.StringIO('a'), io.BytesIO(b'b'))


def test_iterutils():
    assert list(flatten_iter([1, [2, [3, 'ab']]])) == [1, 2, 3, 'ab']
    assert list(rstrip_iter([1, None, 2, None, None])) == [1, None, 2]
    e = PathAccessError(KeyError('k'), 'seg', ('p',))
    assert repr(e) == "PathAccessError(KeyError('k'), 'seg', ('p',))"
    g = SequentialGUIDerator()
    assert next(g) != next(g)


def test_listutils_setutils_mathutils():
    bl = BarrelList([3, 1, 2])
    assert repr(bl) == 'BarrelList([3, 1, 2])'
    with pytest.raises(ValueError, match='9 is not in list'):
        bl.index(9)
    s = IndexedSet([1, 2])
    assert repr(s) == 'IndexedSet([1, 2])'
    with pytest.raises(ValueError, match='5 is not in IndexedSet'):
        s.index(5)
    assert repr(complement({1})) == 'complement({1})'
    b = Bits('1010')
    assert repr(b) == "Bits('1010')"
    assert b.as_hex() == '0A'
    with pytest.raises(TypeError, match='initialized with bad type: float'):
        Bits(1.5)
    with pytest.raises(ValueError, match='value 300 cannot be represented with 4 bits'):
        Bits(300, 4)


def test_socketutils_messages():
    assert str(MessageTooLong(5, b'\n')) == (
        "message exceeded maximum size. 5 bytes read. Delimiter not found: b'\\n'")
    assert str(NetstringMessageTooLong(5, 3)) == (
        'netstring message length exceeds configured maxsize: 5 > 3')


def test_statsutils_text():
    out = Stats([1, 2, 3]).describe(format='text')
    assert out.splitlines()[0].startswith('count:    3')


def test_strutils():
    assert unit_len([1, 2], 'cat') == '2 cats'
    assert unit_len([], 'cat') == 'No cats'
    assert a10n('hello') == 'h3o'
    assert format_int_list([1, 2, 3, 5, 7, 8]) == '1-3,5,7-8'
    assert format_int_list([1, 2, 3, 5, 7, 8], delim_space=True) == '1-3, 5, 7-8'
    mr = MultiReplace([('a', 'b'), ('c', 'd')])
    assert mr.sub('aacc') == 'bbdd'
    assert asciify('Æsir ß', ignore=True) == b'AEsir ss'


def test_tableutils_tbutils_timeutils():
    t = Table([[1, 2]], headers=['a', 'b'])
    assert repr(t) == "Table(headers=['a', 'b'], data=[[1, 2]])"
    assert repr(Table()) == 'Table([])'
    pe = ParsedException.from_string(
        'Traceback (most recent call last):\n'
        '  File "x.py", line 3, in f\n'
        '    foo()\n'
        'ValueError: bad')
    assert pe.to_string() == (
        'Traceback (most recent call last):\n'
        '  File "x.py", line 3, in f\n'
        '    foo()\n'
        'ValueError: bad')


def test_urlutils():
    u = URL('http://a.com/x/../y/./z?q=1#f')
    assert (u.normalize() or u).to_text() == 'http://a.com/y/z?q=1#f'
    assert URL('http://u:p@h:8/a%20b').path == '/a b'
    assert URL('urn:isbn:1').scheme == 'urn'
    assert URL('http://a.com/é').to_text(full_quote=True) == 'http://a.com/%C3%A9'
