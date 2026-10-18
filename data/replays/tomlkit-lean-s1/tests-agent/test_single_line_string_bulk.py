import pytest

from tomlkit import loads
from tomlkit.exceptions import InvalidControlChar
from tomlkit.exceptions import UnexpectedEofError


@pytest.mark.parametrize(
    "src, expected",
    [
        ('a = "hello world"', "hello world"),
        ("a = 'hello world'", "hello world"),
        ('a = "ab\\ncd\\"ef\\\\gh"', 'ab\ncd"ef\\gh'),
        ("a = 'ab\\ncd\"ef'", 'ab\\ncd"ef'),
        ('a = "tab\there"', "tab\there"),
        ("a = 'tab\there'", "tab\there"),
        ('a = "\\u00e9 é 日本"', "é é 日本"),
        ('a = ""', ""),
        ("a = 'it'", "it"),
        ('a = "x' + "y" * 10000 + '"', "x" + "y" * 10000),
    ],
)
def test_single_line_string_values(src, expected):
    doc = loads(src)
    assert doc["a"] == expected
    assert doc.as_string() == src


@pytest.mark.parametrize("ch", ["\x00", "\x01", "\x1f", "\x7f", "\n", "\r"])
def test_control_char_error_type(ch):
    with pytest.raises(InvalidControlChar):
        loads(f'a = "abc{ch}def"')
    with pytest.raises(InvalidControlChar):
        loads(f"a = 'abc{ch}def'")


@pytest.mark.parametrize("src", ['a = "abc', "a = 'abc", 'a = "abc\\', 'a = "'])
def test_unterminated_string_eof(src):
    with pytest.raises(UnexpectedEofError):
        loads(src)
