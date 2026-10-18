import pytest

import tomlkit


DOC = """\
a = 1
[x]
y = 1
[x.z]
w = 2
[o]
t = {k = 1}
"""


def test_container_contains():
    doc = tomlkit.parse(DOC)
    assert "a" in doc
    assert "missing" not in doc
    assert "x" in doc
    assert tomlkit.key("a") in doc
    assert tomlkit.key("nope") not in doc


def test_container_contains_non_str_raises_type_error():
    doc = tomlkit.parse(DOC)
    with pytest.raises(TypeError):
        1 in doc  # noqa: B015


def test_table_contains():
    doc = tomlkit.parse(DOC)
    assert "y" in doc["x"]
    assert "z" in doc["x"]
    assert "nope" not in doc["x"]


def test_inline_table_contains():
    doc = tomlkit.parse(DOC)
    assert "k" in doc["o"]["t"]
    assert "nope" not in doc["o"]["t"]


def test_dotted_key_contains():
    doc = tomlkit.parse("a.b = 1\n")
    assert "a" in doc
    assert "b" in doc["a"]
    assert "c" not in doc["a"]


def test_out_of_order_contains():
    doc = tomlkit.parse("[a.b]\nx = 1\n[c]\ny = 1\n[a.d]\nz = 1\n")
    assert "a" in doc
    assert "b" in doc["a"]
    assert "d" in doc["a"]
    assert "e" not in doc["a"]
