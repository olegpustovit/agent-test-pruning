import pytest

from tomlkit import inline_table
from tomlkit import loads
from tomlkit import table
from tomlkit import dumps


def test_append_table_rejected():
    it = inline_table()
    with pytest.raises(ValueError, match="Inline tables cannot contain a table"):
        it.append("a", table())
    assert dumps({"x": it}) == "x = {}\n"


def test_setitem_table_rejected():
    it = inline_table()
    with pytest.raises(ValueError, match="Inline tables cannot contain a table"):
        it["a"] = table()
    assert "a" not in it


def test_setitem_table_rejected_on_parsed_inline_table():
    doc = loads("x = {a = 1}\n")
    with pytest.raises(ValueError):
        doc["x"]["b"] = table()
    assert doc.as_string() == "x = {a = 1}\n"


def test_regular_values_still_allowed():
    it = inline_table()
    it["a"] = 1
    it["b"] = {"c": 2}
    it.append("d", [1, 2])
    assert it.unwrap() == {"a": 1, "b": {"c": 2}, "d": [1, 2]}
    assert loads(dumps({"x": it}))["x"] == {"a": 1, "b": {"c": 2}, "d": [1, 2]}


def test_nested_inline_table_allowed():
    it = inline_table()
    inner = inline_table()
    inner["z"] = 1
    it["inner"] = inner
    assert dumps({"x": it}) == "x = {inner = {z = 1}}\n"
