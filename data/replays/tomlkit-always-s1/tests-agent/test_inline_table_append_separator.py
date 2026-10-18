import pytest

from tomlkit import loads
from tomlkit import parse


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("a = {x = 1, y = 2}\n", "a = {x = 1, y = 2, z = 3}\n"),
        ("a = { foo = 1, bar = 2 }\n", "a = { foo = 1, bar = 2, z = 3}\n"),
        ("a = { a = 1 }\n", "a = { a = 1, z = 3}\n"),
        ("a = {a = 1}\n", "a = {a = 1,z = 3}\n"),
        ("a = {x = 1,y = 2}\n", "a = {x = 1,y = 2, z = 3}\n"),
    ],
)
def test_append_to_inline_table_separator(text, expected):
    doc = parse(text)
    doc["a"]["z"] = 3
    assert doc.as_string() == expected
    assert loads(doc.as_string())["a"]["z"] == 3


def test_no_double_space_after_comma():
    doc = parse("a = { foo = 1, bar = 2 }\n")
    doc["a"]["z"] = 3
    assert ",  " not in doc.as_string()
