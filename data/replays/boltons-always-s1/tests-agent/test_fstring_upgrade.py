import datetime
import pytest

from boltons.cacheutils import LRU, cachedproperty, cached, make_cache_key
from boltons.dictutils import OMD, OneToOne, ManyToMany, FrozenDict
from boltons.ecoutils import get_profile
from boltons.fileutils import AtomicSaver
from boltons.formatutils import infer_positional_format_args, BaseFormatField
from boltons.funcutils import format_invocation, FunctionBuilder, ExistingArgument, format_nonexp_repr
from boltons.iterutils import PathAccessError
from boltons.listutils import BarrelList
from boltons.mathutils import Bits
from boltons.setutils import IndexedSet, complement
from boltons.socketutils import MessageTooLong
from boltons.strutils import unit_len, a10n, format_int_list, MultiReplace
from boltons.tableutils import Table
from boltons.tbutils import ExceptionInfo, ParsedException
from boltons.timeutils import relative_time, ConstantTZInfo
from boltons.typeutils import make_sentinel
from boltons.urlutils import URL, parse_host, URLParseError, _make_quote_map
from boltons.urlutils import cachedproperty as url_cp


def test_cache_reprs():
    k = make_cache_key((1, 2), {})
    assert repr(k).startswith('_HashedKey([')

    @cached({})
    def f(x):
        return x
    assert repr(f) == 'CachedFunction(func=%r)' % f.func

    class A:
        @cachedproperty
        def p(self):
            return 1
    assert repr(A.__dict__['p']) == '<cachedproperty func=%s>' % A.__dict__['p'].func


def test_dict_reprs():
    assert repr(OMD([(1, 2), (1, 3)])) == 'OrderedMultiDict([(1, 2), (1, 3)])'
    assert repr(OneToOne({1: 2})) == 'OneToOne({1: 2})'
    assert repr(ManyToMany([(1, 2)])) == 'ManyToMany([(1, 2)])'
    assert repr(FrozenDict({1: 2})) == 'FrozenDict({1: 2})'


def test_unexpected_kwargs():
    with pytest.raises(TypeError, match='unexpected keyword arguments'):
        get_profile(bogus=1)
    with pytest.raises(TypeError, match='unexpected kwargs'):
        AtomicSaver('x', bogus=1)


def test_format():
    assert infer_positional_format_args('a {} {!r:>3} {{x}} {}') == 'a {0} {1!r:>3} {{x}} {2}'
    assert repr(BaseFormatField('a', '>3')) == "BaseFormatField('a', '>3')"


def test_funcutils():
    assert format_invocation('f', (1, 'a'), {'k': 2}) == "f(1, 'a', k=2)"
    assert format_invocation('f') == 'f()'

    class O:
        a = 1
    assert format_nonexp_repr(O(), ['a']) == "<O a=1>"

    fb = FunctionBuilder('f', args=['x'], kwonlyargs=['y'])
    with pytest.raises(ExistingArgument, match=r"arg 'x' already in func f arg list"):
        fb.add_arg('x')
    with pytest.raises(ExistingArgument, match=r"arg 'y' already in func f kwonly arg list"):
        fb.add_arg('y')
    with pytest.raises(TypeError, match='expected callable object, not 5'):
        FunctionBuilder.from_func(5)


def test_misc_reprs():
    e = PathAccessError(KeyError('a'), 'a', ('a',))
    assert repr(e) == "PathAccessError(KeyError('a'), 'a', ('a',))"
    assert repr(BarrelList([1, 2])) == 'BarrelList([1, 2])'
    with pytest.raises(ValueError, match='5 is not in list'):
        BarrelList([1]).index(5)
    assert repr(IndexedSet([1, 2])) == 'IndexedSet([1, 2])'
    with pytest.raises(ValueError, match='3 is not in IndexedSet'):
        IndexedSet([1]).index(3)
    assert repr(complement({1})) == 'complement({1})'
    assert repr(Table([[1, 2]], headers=None)).startswith('Table(')
    assert repr(Table([[1, 2]], headers=['a', 'b'])).startswith("Table(headers=['a', 'b'], data=")
    S = make_sentinel('X')
    assert repr(S) == "Sentinel('X')"
    tz = ConstantTZInfo('UTC')
    assert repr(tz) == "ConstantTZInfo(name='UTC', offset=%r)" % tz.offset


def test_bits():
    b = Bits('1011')
    assert b.as_bin() == '1011'
    assert b.as_hex() == '0B'
    assert repr(b) == "Bits('1011')"
    assert Bits(5).as_bin() == '101'
    assert Bits('1' * 9).as_hex() == '01FF'
    with pytest.raises(TypeError, match='initialized with bad type: float'):
        Bits(1.5)
    with pytest.raises(ValueError, match='value 9 cannot be represented with 2 bits'):
        Bits(9, 2)


def test_socket_msg():
    assert str(MessageTooLong(5, b'\n')) == (
        "message exceeded maximum size. 5 bytes read. Delimiter not found: b'\\n'")


def test_strutils():
    assert unit_len([1, 2], 'item') == '2 items'
    assert unit_len([], 'item') == 'No items'
    assert a10n('abcdef') == 'a4f'
    assert format_int_list([1, 2, 3, 5, 7, 8, 9]) == '1-3,5,7-9'
    assert format_int_list([1, 3]) == '1,3'
    assert MultiReplace([('a', 'b'), ('c', 'd')]).sub('acx') == 'bdx'


def test_tbutils():
    try:
        raise ValueError('boom')
    except ValueError as e:
        ei = ExceptionInfo.from_exc_info(type(e), e, e.__traceback__)
    assert ei.exc_type == 'ValueError'
    assert ei.get_formatted_exception_only() == 'ValueError: boom'
    assert ei.get_formatted().endswith('ValueError: boom')
    assert '<TracebackInfo frames=1 last=' in repr(ei.tb_info)
    assert ', last=' in repr(ei)
    assert ei.tb_info.frames[0].tb_frame_str().rstrip().endswith("raise ValueError('boom')")
    pe = ParsedException('KeyError', 'k', [])
    assert pe.to_string().endswith('\nKeyError: k')
    assert ParsedException('KeyError', '', []).to_string().endswith('\nKeyError')
    pe = ParsedException('E', 'm', [{'filepath': 'f.py', 'lineno': '3', 'funcname': 'g',
                                     'source_line': 'x = 1'}])
    assert '    x = 1' in pe.to_string()


def test_relative_time():
    now = datetime.datetime(2020, 1, 1, 12)
    assert relative_time(now - datetime.timedelta(hours=3), now) == '3 hours ago'
    assert relative_time(now + datetime.timedelta(hours=3), now) == '3 hours from now'


def test_url():
    u = URL('http://a.com/b?c=d')
    assert repr(u) == "URL('http://a.com/b?c=d')"
    assert _make_quote_map('')[' '] == '%20'
    assert _make_quote_map('')['\x0a'] == '%0A'
    with pytest.raises(URLParseError, match='invalid IPv6 host'):
        parse_host('[::zz::]')
    assert url_cp.__name__ == 'cachedproperty'
