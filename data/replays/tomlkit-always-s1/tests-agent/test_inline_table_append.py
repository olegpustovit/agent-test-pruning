import pytest

import tomlkit


@pytest.mark.parametrize(
    "text",
    ["a = {x = 1, y = 2}", "a = {x = 1}", "a = { x = 1 , y = 2 }"],
)
def test_append_to_parsed_inline_table_roundtrips(text):
    doc = tomlkit.parse(text)
    expected = dict(doc["a"])
    doc["a"]["z"] = 3
    expected["z"] = 3
    out = doc.as_string()
    assert tomlkit.parse(out)["a"] == expected


def test_append_twice():
    doc = tomlkit.parse("a = {x = 1, y = 2}")
    doc["a"]["z"] = 3
    doc["a"]["w"] = 4
    assert tomlkit.parse(doc.as_string())["a"] == {"x": 1, "y": 2, "z": 3, "w": 4}
