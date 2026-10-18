from tomlkit import dumps
from tomlkit import parse


def test_unwrap_order_after_replace():
    doc = parse("a = 1\nb = 2\nc = 3\n")
    doc["b"] = 9
    assert dumps(doc) == "a = 1\nb = 9\nc = 3\n"
    assert list(doc.keys()) == ["a", "b", "c"]
    assert list(doc.unwrap()) == ["a", "b", "c"]


def test_unwrap_order_after_replace_first_and_last():
    doc = parse("a = 1\nb = 2\nc = 3\n")
    doc["a"] = 5
    doc["c"] = 6
    assert list(doc.unwrap().items()) == [("a", 5), ("b", 2), ("c", 6)]


def test_unwrap_order_in_table():
    doc = parse("[t]\na = 1\nb = 2\nc = 3\n")
    doc["t"]["a"] = 7
    assert list(doc.unwrap()["t"].items()) == [("a", 7), ("b", 2), ("c", 3)]


def test_unwrap_order_follows_body_when_element_moves():
    doc = parse("a = 1\nb = 2\n[t]\nx = 1\n")
    doc["b"] = {"k": 1}
    assert dumps(doc) == "a = 1\n[b]\nk = 1\n\n[t]\nx = 1\n"
    assert list(doc.unwrap()) == list(parse(dumps(doc)).unwrap())
    assert doc.unwrap() == {"a": 1, "b": {"k": 1}, "t": {"x": 1}}
