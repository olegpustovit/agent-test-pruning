import pytest

import tomlkit

from tomlkit import inline_table
from tomlkit import table


def test_append_table_rejected():
    t = inline_table()
    with pytest.raises(ValueError, match="Inline tables cannot contain a table"):
        t.append("a", table())
    assert "a" not in t


def test_setitem_table_rejected():
    t = inline_table()
    with pytest.raises(ValueError, match="Inline tables cannot contain a table"):
        t["a"] = table()
    assert "a" not in t


def test_setitem_on_parsed_inline_table_rejected():
    doc = tomlkit.parse("x = {a = 1}")
    with pytest.raises(ValueError):
        doc["x"]["b"] = table()
    assert doc.as_string() == "x = {a = 1}"


def test_dict_value_becomes_inline_table():
    t = inline_table()
    t["a"] = {"x": 1}
    assert t.as_string() == "{a = {x = 1}}"


def test_plain_values_still_work():
    t = inline_table()
    t["a"] = 1
    t.append("b", "s")
    assert t.as_string() == '{a = 1, b = "s"}'
