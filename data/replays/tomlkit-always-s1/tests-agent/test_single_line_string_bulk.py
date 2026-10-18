import pytest

from tomlkit import loads
from tomlkit.exceptions import InvalidControlChar
from tomlkit.exceptions import UnexpectedEofError
from tomlkit.exceptions import ParseError


@pytest.mark.parametrize(
    "src, expected",
    [
        ('a = "hello world"', "hello world"),
        ('a = ""', ""),
        ("a = 'hello \\n world'", "hello \\n world"),
        ('a = "x\\ty\\\\z\\"w"', 'x\ty\\z"w'),
        ('a = "tab\there"', "tab\there"),
        ("a = 'it\"s'", 'it"s'),
        ('a = "it\'s"', "it's"),
        ('a = "\\u00e9abc\\U0001F600def"', "éabc😀def"),
        ('a = "' + "x" * 10000 + '"', "x" * 10000),
        ("a = '" + "y" * 10000 + "'", "y" * 10000),
        ('a = "' + "ab\\n" * 500 + '"', "ab\n" * 500),
    ],
)
def test_single_line_values(src, expected):
    assert loads(src)["a"] == expected
    assert loads(src).as_string() == src


@pytest.mark.parametrize("ch", ["\x00", "\x01", "\x08", "\x0b", "\x1f", "\x7f"])
@pytest.mark.parametrize("q", ['"', "'"])
def test_control_char_mid_run(ch, q):
    with pytest.raises(InvalidControlChar):
        loads(f"a = {q}abc{ch}def{q}")
    with pytest.raises(InvalidControlChar):
        loads(f"a = {q}{ch}{q}")


@pytest.mark.parametrize("q", ['"', "'"])
def test_newline_in_single_line_string(q):
    with pytest.raises(ParseError):
        loads(f"a = {q}abc\ndef{q}")
    with pytest.raises(ParseError):
        loads(f"a = {q}abc\r\ndef{q}")


@pytest.mark.parametrize("src", ['a = "abc', "a = 'abc", 'a = "abc\\', 'a = "'])
def test_unterminated(src):
    with pytest.raises(UnexpectedEofError):
        loads(src)


def test_multiline_unchanged():
    assert loads('a = """x\r\ny\\\n  z"""')["a"] == "x\r\nyz"
    assert loads("a = '''x\ny'''")["a"] == "x\ny"


def test_following_content_parsed():
    doc = loads('a = "x y"\nb = \'z\'  # c\nc = ["p", \'q\']\n')
    assert doc["a"] == "x y" and doc["b"] == "z" and doc["c"] == ["p", "q"]
