import pytest

import tomlkit

from tomlkit.container import ends_with_whitespace
from tomlkit.items import Whitespace


@pytest.mark.parametrize(
    "doc, expected",
    [
        ("[a.b]\nx = 1\n\n[c]\ny = 1\n", True),
        ("[a.b.c]\nx = 1\n\n[d]\ny = 1\n", True),
        ("[a.b]\nx = 1\n[c]\ny = 1\n", False),
    ],
)
def test_super_table_ends_with_whitespace(doc, expected):
    parsed = tomlkit.parse(doc)
    assert ends_with_whitespace(parsed["a"]) is expected


def test_ends_with_whitespace_basic():
    assert ends_with_whitespace(Whitespace("\n"))
    assert not ends_with_whitespace(tomlkit.table())
    assert not ends_with_whitespace(1)
    assert not ends_with_whitespace(tomlkit.aot())


@pytest.mark.parametrize(
    "doc, key, value, expected",
    [
        (
            "[a.b]\nx = 1\n\n[c]\ny = 1\n",
            "a",
            {"b": {"x": 2}},
            "[a.b]\nx = 2\n\n[c]\ny = 1\n",
        ),
        (
            "[a.b.c]\nx = 1\n\n[d]\ny = 1\n",
            "a",
            {"b": {"c": {"x": 2}}},
            "[a.b.c]\nx = 2\n\n[d]\ny = 1\n",
        ),
    ],
)
def test_replace_super_table_preserves_blank_line(doc, key, value, expected):
    parsed = tomlkit.parse(doc)
    parsed[key] = value
    assert parsed.as_string() == expected
