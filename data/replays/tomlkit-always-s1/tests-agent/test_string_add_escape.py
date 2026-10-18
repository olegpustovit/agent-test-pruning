import tomlkit

from tomlkit.items import String
from tomlkit.items import StringType


def test_basic_add_escapes_quote_and_backslash():
    s = tomlkit.string("a") + '"\\b'
    assert s == 'a"\\b'
    assert s.as_string() == '"a\\"\\\\b"'
    assert tomlkit.parse("x = " + s.as_string())["x"] == 'a"\\b'


def test_basic_add_newline():
    s = tomlkit.string("a") + "\n"
    assert tomlkit.parse("x = " + s.as_string())["x"] == "a\n"


def test_add_string_keeps_escaped_raw():
    a = tomlkit.string("a")
    b = tomlkit.string('"q"')
    s = a + b
    assert s.as_string() == '"a\\"q\\""'
    assert tomlkit.parse("x = " + s.as_string())["x"] == 'a"q"'


def test_literal_string_not_escaped():
    s = String.from_raw("a\\b", StringType.SLL) + "\\c"
    assert s.as_string() == "'a\\b\\c'"
    assert tomlkit.parse("x = " + s.as_string())["x"] == "a\\b\\c"


def test_multiline_basic_add():
    s = String.from_raw("a", StringType.MLB) + '\\"'
    assert tomlkit.parse("x = " + s.as_string())["x"] == 'a\\"'


def test_plain_add_unchanged():
    s = tomlkit.string("a") + "bc"
    assert s.as_string() == '"abc"'
