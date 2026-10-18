from tomlkit import dumps
from tomlkit import loads
from tomlkit import table


def test_unwrap_order_kept_after_value_replaced():
    doc = loads("a = 1\nb = 2\nc = 3\n")
    doc["b"] = 9
    assert dumps(doc) == "a = 1\nb = 9\nc = 3\n"
    assert list(doc.unwrap()) == ["a", "b", "c"]
    assert doc.unwrap() == {"a": 1, "b": 9, "c": 3}


def test_unwrap_order_kept_after_replacing_first_key():
    doc = loads("a = 1\nb = 2\nc = 3\n")
    doc["a"] = 5
    assert list(doc.unwrap()) == ["a", "b", "c"]


def test_unwrap_order_in_nested_table_after_replace():
    doc = loads("[t]\nx = 1\ny = 2\nz = 3\n")
    doc["t"]["x"] = 10
    assert list(doc["t"].unwrap()) == ["x", "y", "z"]
    assert list(doc.unwrap()["t"]) == ["x", "y", "z"]


def test_unwrap_follows_body_when_bare_key_promoted_to_table():
    doc = loads("a = 1\nb = {x = 1}\nc = 3\n")
    doc["a"] = table()
    assert dumps(doc) == "b = {x = 1}\nc = 3\n\n[a]\n"
    assert list(doc.unwrap()) == ["b", "c", "a"]
