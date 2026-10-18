import tomlkit

from tomlkit.items import String
from tomlkit.items import StringType


def test_add_escapes_quote_and_backslash_basic():
    s = tomlkit.string("abc")
    r = s + 'x"y\\z'
    assert isinstance(r, String)
    assert r == 'abcx"y\\z'
    assert r.as_string() == '"abcx\\"y\\\\z"'
    assert tomlkit.parse("a = " + r.as_string())["a"] == 'abcx"y\\z'


def test_add_string_operand_keeps_escaped_form():
    r = tomlkit.string("a") + tomlkit.string('"b')
    assert r.as_string() == '"a\\"b"'
    assert tomlkit.loads("a = " + r.as_string())["a"] == 'a"b'


def test_add_literal_string_not_escaped():
    s = tomlkit.string("a", literal=True)
    r = s + "\\b"
    assert r.as_string() == "'a\\b'"
    assert tomlkit.loads("a = " + r.as_string())["a"] == "a\\b"


def test_add_multiline_basic():
    s = tomlkit.string("a", multiline=True)
    r = s + '"\\'
    assert tomlkit.loads("a = " + r.as_string())["a"] == 'a"\\'
