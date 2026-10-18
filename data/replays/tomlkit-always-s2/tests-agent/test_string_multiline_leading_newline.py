import pytest

import tomlkit

from tomlkit.items import StringType


@pytest.mark.parametrize("literal", [False, True])
@pytest.mark.parametrize("value", ["\nfoo", "\n\nfoo", "\r\nfoo", "\nfoo\nbar\n"])
def test_multiline_leading_newline_roundtrip(value, literal):
    s = tomlkit.string(value, multiline=True, literal=literal)
    assert str(s) == value
    doc = tomlkit.parse(f"k = {s.as_string()}")
    assert doc["k"] == value
    assert tomlkit.parse(tomlkit.dumps(doc))["k"] == value


def test_multiline_leading_newline_rendering():
    assert tomlkit.string("\nfoo", multiline=True).as_string() == '"""\n\nfoo"""'
    assert tomlkit.string("\nfoo", multiline=True, literal=True).as_string() == "'''\n\nfoo'''"


def test_unchanged_cases():
    assert tomlkit.string("foo", multiline=True).as_string() == '"""foo"""'
    assert tomlkit.string("\nfoo").as_string() == '"\\nfoo"'
    assert tomlkit.string("", multiline=True).as_string() == '""""""'
    assert tomlkit.string("a\nb", multiline=True).as_string() == '"""a\nb"""'
