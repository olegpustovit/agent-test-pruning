import time

import pytest

from tomlkit import parse
from tomlkit.exceptions import ParseError


def test_duplicate_key_in_out_of_order_table_raises():
    doc = """[a.b]
x = 1
[c]
y = 1
[a.b]
x = 2
"""
    with pytest.raises(ParseError, match="already exists"):
        parse(doc)


def test_duplicate_key_in_split_super_table_raises():
    doc = """[a]
x = 1
[b]
y = 1
[a]
x = 2
"""
    with pytest.raises(ParseError, match="already exists"):
        parse(doc)


def test_out_of_order_nested_tables_parse_and_access():
    doc = """[a.b]
x = 1
[c]
y = 1
[a.d]
z = 2
"""
    d = parse(doc)
    assert d["a"]["b"]["x"] == 1
    assert d["a"]["d"]["z"] == 2
    assert d.as_string() == doc


def test_many_nested_tables_parse_quickly():
    doc = "".join(f"[a.t{i}]\nx = {i}\n" for i in range(200))
    start = time.time()
    d = parse(doc)
    assert time.time() - start < 10
    assert len(d["a"]) == 200


def test_deeper_nested_out_of_order_tables_are_kept():
    doc = """[tool.a.b]
x = 1
[other]
y = 1
[tool.a.c]
z = 2
[tool.d]
w = 3
"""
    d = parse(doc)
    assert d["tool"]["a"]["b"] == {"x": 1}
    assert d["tool"]["a"]["c"] == {"z": 2}
    assert d["tool"]["d"] == {"w": 3}
    d["tool"]["a"]["b"]["x"] = 5
    assert d["tool"]["a"]["b"]["x"] == 5
    assert d.as_string() == doc.replace("x = 1", "x = 5")
