import pytest

from tomlkit import parse
from tomlkit.exceptions import InvalidControlChar
from tomlkit.exceptions import UnexpectedEofError
from tomlkit.exceptions import ParseError


@pytest.mark.parametrize(
    "src, expected",
    [
        ('a = "hello world"', "hello world"),
        ("a = 'hello world'", "hello world"),
        ('a = ""', ""),
        ("a = ''", ""),
        ('a = "ab\\tcd\\"ef\\\\gh"', 'ab\tcd"ef\\gh'),
        ("a = 'ab\\tcd\"ef'", 'ab\\tcd"ef'),
        ('a = "tab\there"', "tab\there"),
        ("a = 'tab\there'", "tab\there"),
        ('a = "\\u00e9x\\U0001F600y"', "éx\U0001f600y"),
        ('a = "héllo ☃ 😀"', "héllo ☃ 😀"),
        ("a = '" + "x" * 10000 + "'", "x" * 10000),
        ('a = "' + "xy\\n" * 1000 + '"', "xy\n" * 1000),
        ('a = "it\'s"', "it's"),
        ("a = 'say \"hi\"'", 'say "hi"'),
    ],
)
def test_single_line_values(src, expected):
    doc = parse(src)
    assert doc["a"] == expected
    assert doc.as_string() == src


def test_multiline_unchanged():
    doc = parse('a = """x\r\ny\\\n   z"""\nb = \'\'\'p\nq\'\'\'')
    assert doc["a"] == "x\r\nyz"
    assert doc["b"] == "p\nq"


@pytest.mark.parametrize("ch", ["\x00", "\x01", "\x08", "\x0b", "\x1f", "\x7f", "\n", "\r"])
@pytest.mark.parametrize("q", ['"', "'"])
def test_control_chars_rejected(ch, q):
    with pytest.raises(ParseError):
        parse(f"a = {q}ab{ch}cd{q}")


@pytest.mark.parametrize("ch", ["\x00", "\x7f", "\x1f"])
def test_control_char_error_type(ch):
    with pytest.raises(InvalidControlChar):
        parse(f'a = "abc{ch}def"')
    with pytest.raises(InvalidControlChar):
        parse(f"a = 'abc{ch}def'")


@pytest.mark.parametrize("src", ['a = "abc', "a = 'abc", 'a = "abc\\', 'a = "', "a = '"])
def test_unterminated(src):
    with pytest.raises(ParseError):
        parse(src)


@pytest.mark.parametrize("src", ['a = "abc', "a = 'abc"])
def test_unterminated_eof_error(src):
    with pytest.raises(UnexpectedEofError):
        parse(src)


def test_invalid_escape():
    with pytest.raises(ParseError):
        parse('a = "ab\\qcd"')


def test_keys_and_arrays():
    doc = parse('"k e y" = ["a b", \'c d\']\n\'x\' = {i = "j k"}')
    assert doc["k e y"] == ["a b", "c d"]
    assert doc["x"]["i"] == "j k"
