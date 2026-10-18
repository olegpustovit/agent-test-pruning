import pytest

import tomlkit


def test_dumps_deeply_nested_subtable():
    doc = tomlkit.parse("[a.b.c.d]\nx = 1\ny = 2\n")
    sub = doc["a"]["b"]["c"]["d"]
    assert tomlkit.dumps(sub) == "x = 1\ny = 2\n"


def test_dumps_dotted_key_subtable():
    doc = tomlkit.parse("a.b.c.d = 1\na.b.c.e = 2\n")
    out = tomlkit.dumps(doc["a"]["b"]["c"])
    assert "d = 1" in out and "e = 2" in out


def test_dumps_inline_table():
    doc = tomlkit.parse("a = {b = 1}\n")
    assert "b = 1" in tomlkit.dumps(doc["a"])


def test_dumps_invalid_type_message():
    with pytest.raises(TypeError):
        tomlkit.dumps(object())
