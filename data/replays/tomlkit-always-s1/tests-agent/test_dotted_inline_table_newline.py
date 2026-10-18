import pytest

import tomlkit


@pytest.mark.parametrize("op", ["setitem", "append", "add"])
def test_newline_kept_after_dotted_inline_table_without_trailing_newline(op):
    doc = tomlkit.parse("a.b = {x = 1}")
    if op == "setitem":
        doc["z"] = 2
    else:
        getattr(doc, op)("z", 2)
    assert doc.as_string() == "a.b = {x = 1}\nz = 2\n"
    assert tomlkit.parse(doc.as_string()) == {"a": {"b": {"x": 1}}, "z": 2}


def test_trailing_newline_not_duplicated():
    doc = tomlkit.parse("a.b = {x = 1}\n")
    doc["z"] = 2
    assert doc.as_string() == "a.b = {x = 1}\nz = 2\n"


def test_other_items_unaffected():
    doc = tomlkit.parse("x = 1\na.b = {x = 1}\n")
    doc["z"] = 2
    assert doc.as_string() == "x = 1\na.b = {x = 1}\nz = 2\n"
