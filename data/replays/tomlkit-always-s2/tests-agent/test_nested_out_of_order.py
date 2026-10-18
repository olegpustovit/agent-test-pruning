import pytest

from tomlkit import dumps, parse
from tomlkit.exceptions import ParseError

DOC = """\
[a.b]
x = 1

[c]
y = 2

[a.d.e]
z = 3

[a]
w = 4
"""


def test_nested_out_of_order_table_is_kept():
    doc = parse(DOC)
    assert doc["a"]["b"]["x"] == 1
    assert doc["a"]["d"]["e"]["z"] == 3
    assert doc["a"]["w"] == 4
    assert doc == {
        "a": {"b": {"x": 1}, "d": {"e": {"z": 3}}, "w": 4},
        "c": {"y": 2},
    }
    assert dumps(doc) == DOC


def test_nested_out_of_order_table_survives_modification():
    doc = parse(DOC)
    doc["a"]["d"]["e"]["z"] = 5
    doc["a"]["b"]["n"] = 1
    out = dumps(doc)
    assert parse(out) == {
        "a": {"b": {"x": 1, "n": 1}, "d": {"e": {"z": 5}}, "w": 4},
        "c": {"y": 2},
    }


def test_out_of_order_duplicate_still_rejected():
    with pytest.raises(ParseError):
        parse("[a.b]\nx=1\n[c]\ny=1\n[a]\nq=1\n[a]\nq=2\n")
