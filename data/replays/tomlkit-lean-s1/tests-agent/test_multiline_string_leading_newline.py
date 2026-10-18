import pytest

import tomlkit

from tomlkit.items import StringType


@pytest.mark.parametrize(
    "value",
    ["\nfoo", "\n\nfoo", "\r\nfoo", "\n", "\nfoo\nbar"],
)
@pytest.mark.parametrize("literal", [False, True])
def test_multiline_leading_newline_round_trip(value, literal):
    s = tomlkit.string(value, multiline=True, literal=literal)
    assert str(s) == value
    parsed = tomlkit.parse(f"k = {s.as_string()}")
    assert parsed["k"] == value
    assert parsed.as_string() == f"k = {s.as_string()}"


def test_multiline_leading_newline_rendering():
    assert tomlkit.string("\nfoo", multiline=True).as_string() == '"""\n\nfoo"""'
    assert tomlkit.string("\nfoo", multiline=True, literal=True).as_string() == "'''\n\nfoo'''"


def test_no_extra_newline_otherwise():
    assert tomlkit.string("foo\n", multiline=True).as_string() == '"""foo\n"""'
    assert tomlkit.string("\nfoo").as_string() == '"\\nfoo"'
