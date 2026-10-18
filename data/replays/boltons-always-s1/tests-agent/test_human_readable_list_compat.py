import inspect

from boltons import strutils
from boltons.strutils import human_readable_list as hrl


def test_basic():
    assert hrl([]) == ''
    assert hrl(['a']) == 'a'
    assert hrl(['a', 'b']) == 'a and b'
    assert hrl(['a', 'b', 'c']) == 'a, b, and c'


def test_non_oxford():
    assert hrl(['a', 'b', 'c'], oxford=False) == 'a, b and c'
    assert hrl(['a', 'b', 'c', 'd'], oxford=False) == 'a, b, c and d'


def test_delimiter_whitespace_stripped():
    assert hrl(['a', 'b', 'c'], delimiter=' ; ') == 'a; b; and c'
    assert hrl(['a', 'b', 'c'], delimiter=';', conjunction=' or ') == 'a; b; or c'


def test_empty_delimiter():
    assert hrl(['a', 'b', 'c'], delimiter='') == 'aband c'
    assert hrl(['a', 'b', 'c'], delimiter='', oxford=False) == 'ab and c'


def test_no_same_quote_nesting_in_fstring():
    # Source must not use PEP 701 (3.12+) same-quote nesting in f-strings.
    src = inspect.getsource(strutils.human_readable_list)
    assert "{delimiter if oxford else ' '}" not in src
