import re

from boltons.strutils import MultiReplace, multi_replace


def test_basic_and_order():
    assert multi_replace('The foo bar cat ate a bat',
                         [('foo', 'zoo'), ('cat', 'hat'), ('bat', 'kraken')]
                         ) == 'The zoo bar hat ate a kraken'
    m = MultiReplace([('foo', 'baz'), ('baz', 'bar')])
    assert m.sub('foo bar baz') == 'baz bar bar'


def test_regex_with_inner_groups():
    m = MultiReplace([(r'(a)(b)', 'X'), (r'(c)|(d)', 'Y')], regex=True)
    assert m.sub('ab c d ab') == 'X Y Y X'


def test_compiled_pattern_and_flags():
    m = MultiReplace([(re.compile(r'f(o+)'), 'F'), ('bar', 'B')], flags=re.I)
    assert m.sub('FOO Bar') == 'F B'


def test_many_alternatives():
    pairs = [(f'k{i}', str(i)) for i in range(50)]
    m = MultiReplace(pairs)
    assert m.sub(' '.join(k for k, _ in pairs)) == ' '.join(str(i) for i in range(50))


def test_empty_match_replacement():
    m = MultiReplace([(r'x*', '-')], regex=True)
    assert m.sub('ab') == '-a-b-'


def test_falsey_replacement_value():
    assert MultiReplace([('a', '')]).sub('banana') == 'bnn'
