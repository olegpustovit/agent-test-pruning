import tomlkit

from tomlkit.items import String
from tomlkit.items import StringType


def test_basic_add_escapes_quote_and_backslash():
    s = tomlkit.string("a") + '"b\\'
    assert str(s) == 'a"b\\'
    assert s.as_string() == '"a\\"b\\\\"'
    assert tomlkit.parse("x = " + s.as_string())["x"] == 'a"b\\'


def test_basic_add_in_document_roundtrip():
    doc = tomlkit.document()
    doc["k"] = tomlkit.string("pre") + 'say "hi"\n'
    assert tomlkit.parse(tomlkit.dumps(doc))["k"] == 'presay "hi"\n'


def test_literal_add_not_escaped():
    s = tomlkit.string("a", literal=True) + "\\b"
    assert s.as_string() == "'a\\b'"
    assert tomlkit.parse("x = " + s.as_string())["x"] == "a\\b"


def test_string_operand_keeps_escaped_raw():
    a = tomlkit.string("a")
    b = tomlkit.string('"')
    s = a + b
    assert s.as_string() == '"a\\""'
    assert str(s) == 'a"'


def test_plain_add_unchanged():
    s = tomlkit.string("a") + "bc"
    assert s.as_string() == '"abc"'
    assert isinstance(s, String)
