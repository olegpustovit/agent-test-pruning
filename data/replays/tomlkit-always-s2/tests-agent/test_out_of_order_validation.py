import pytest

from tomlkit import dumps
from tomlkit import parse
from tomlkit.container import Container
from tomlkit.exceptions import KeyAlreadyPresent
from tomlkit.exceptions import TOMLKitError
from tomlkit.items import Table


def test_duplicate_key_in_out_of_order_table_rejected():
    doc = """\
[a]
x = 1
[b]
y = 1
[a]
x = 2
"""
    with pytest.raises(TOMLKitError):
        parse(doc)


def test_valid_out_of_order_roundtrip():
    doc = """\
[a.b]
x = 1
[c]
y = 1
[a.d]
z = 1
"""
    parsed = parse(doc)
    assert dumps(parsed) == doc
    assert parsed["a"]["b"]["x"] == 1
    assert parsed["a"]["d"]["z"] == 1
    assert parsed.unwrap() == {"a": {"b": {"x": 1}, "d": {"z": 1}}, "c": {"y": 1}}


def test_getitem_returns_bool_value_and_missing_key():
    doc = parse("a = true\n[t]\nb = false\n")
    assert doc["a"] is True
    assert doc["t"]["b"] is False
    with pytest.raises(KeyError):
        doc["missing"]


def test_container_append_validate_flag():
    c = Container()
    t1 = Table(Container(), None, False)
    c.append("a", t1, validate=False)
    assert "a" in c


def test_table_append_duplicate_still_raises():
    doc = parse("[t]\nx = 1\n")
    with pytest.raises(KeyAlreadyPresent):
        doc["t"].add("x", 2)
