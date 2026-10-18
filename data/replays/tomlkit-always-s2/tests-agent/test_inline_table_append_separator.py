import pytest

from tomlkit import loads
from tomlkit import parse


@pytest.mark.parametrize(
    "text, expected",
    [
        ("a = {x = 1, y = 2}\n", "a = {x = 1, y = 2, z = 3}\n"),
        ("a = {x = 1, y = 2,}\n", "a = {x = 1, y = 2, z = 3}\n"),
        ("a = { x = 1 , y = 2 }\n", "a = { x = 1 , y = 2,  z = 3}\n"),
    ],
)
def test_append_to_inline_table_inserts_separator(text, expected):
    doc = parse(text)
    doc["a"].append("z", 3)
    out = doc.as_string()
    assert out == expected
    assert loads(out)["a"] == {"x": 1, "y": 2, "z": 3}


def test_append_multiple_keeps_valid_toml():
    doc = parse("a = {x = 1, y = 2}\n")
    doc["a"].append("z", 3)
    doc["a"].append("w", 4)
    assert loads(doc.as_string())["a"] == {"x": 1, "y": 2, "z": 3, "w": 4}


def test_unmodified_roundtrip():
    text = "a = { x = 1 , y = 2 , }\n"
    assert parse(text).as_string() == text
