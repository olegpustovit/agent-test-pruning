import re
from collections import OrderedDict

from boltons.strutils import MultiReplace, multi_replace

TEXT = 'The foo bar cat ate a bat'
EXPECTED = 'The zoo bar hat ate a kraken'


def test_multi_replace_docstring_example():
    assert multi_replace(
        TEXT, {'foo': 'zoo', 'cat': 'hat', 'bat': 'kraken'}) == EXPECTED


def test_multi_replace_iterable():
    pairs = [('foo', 'zoo'), ('cat', 'hat'), ('bat', 'kraken')]
    assert MultiReplace(pairs).sub(TEXT) == EXPECTED


def test_multi_replace_regex_and_flags():
    assert multi_replace('Foo 12', {r'f\w+': 'x', r'\d+': 'N'},
                         regex=True, flags=re.I) == 'x N'


def test_multi_replace_escapes_by_default():
    assert multi_replace('a.b axb', {'a.b': 'Z'}) == 'Z axb'


def test_multi_replace_compiled_pattern_and_order():
    m = MultiReplace(OrderedDict([(re.compile('f.o'), 'baz'), ('baz', 'bar')]))
    assert m.sub('foo baz') == 'baz bar'
    assert 'group0' in m.combined_pattern.groupindex
