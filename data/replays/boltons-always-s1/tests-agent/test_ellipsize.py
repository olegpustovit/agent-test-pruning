import pytest

from boltons.strutils import ellipsize


def test_exported():
    import boltons.strutils as s
    assert 'ellipsize' in s.__all__


def test_noop_at_and_below_limit():
    assert ellipsize('Hello, World!', 13) == 'Hello, World!'
    assert ellipsize('Hello, World!', 50) == 'Hello, World!'
    assert ellipsize('', 5) == ''


def test_default_max_len():
    text = 'word ' * 100
    out = ellipsize(text)
    assert len(out) <= 160 and out.endswith('…')
    assert ellipsize('short') == 'short'


def test_cut_at_space():
    out = ellipsize('Beautiful is better than ugly. Explicit is better.', 31)
    assert out == 'Beautiful is better than ugly…'
    assert ellipsize('one two three four', 12) == 'one two…'


def test_trailing_punct_and_space_stripped():
    assert ellipsize('hello, world foo', 9) == 'hello…'
    assert ellipsize('hello;  world foo', 10) == 'hello…'
    assert ellipsize('what? yes it is', 8) == 'what…'


def test_decimal_preserved():
    assert ellipsize('rates around 6.5% this week', 20) == 'rates around 6.5%…'
    assert ellipsize('pi is 3.14 roughly', 12) == 'pi is 3.14…'


def test_sentence_period_stripped():
    assert ellipsize('End of it. More words here', 14) == 'End of it…'


def test_hard_cut():
    assert ellipsize('antidisestablishmentarianism', 10) == 'antidises…'
    assert ellipsize('abcdefghij klm', 6) == 'abcde…'


def test_custom_ellipsis():
    assert ellipsize('one two three four', 13, ellipsis='...') == 'one two...'
    assert ellipsize('abcdefghijkl', 6, ellipsis='..') == 'abcd..'
    assert ellipsize('one two three', 9, ellipsis='') == 'one two'


@pytest.mark.parametrize('ellipsis', ['…', '...', '--'])
def test_max_len_sweep(ellipsis):
    text = 'The quick brown fox, jumps over 3.5 lazy dogs. Really! Yes.'
    for n in range(len(ellipsis) + 1, len(text) + 5):
        out = ellipsize(text, n, ellipsis=ellipsis)
        assert len(out) <= n
        if len(text) <= n:
            assert out == text
        else:
            assert out.endswith(ellipsis)
            assert text.startswith(out[:-len(ellipsis)])


def test_no_mid_word_cut_when_space_available():
    text = 'alpha beta gamma delta epsilon'
    words = set(text.split())
    for n in range(8, len(text)):
        body = ellipsize(text, n)[:-1]
        assert body.split()[-1] in words


def test_value_error():
    with pytest.raises(ValueError):
        ellipsize('hello world', 1)
    with pytest.raises(ValueError):
        ellipsize('hello world', 3, ellipsis='...')
    with pytest.raises(ValueError):
        ellipsize('hi', 0)
    # raised even if text would fit
    with pytest.raises(ValueError):
        ellipsize('a', 1)
