from tomlkit import parse
from tomlkit.items import Bool


def test_bool_items_compare_by_value():
    doc = parse("a = true\nb = true\nc = false\nd = false")
    assert doc["a"] == doc["b"]
    assert doc["c"] == doc["d"]
    assert doc["a"] != doc["c"]
    assert not (doc["a"] == doc["c"])


def test_bool_item_equals_plain_bool():
    doc = parse("a = true\nc = false")
    assert doc["a"] == True  # noqa: E712
    assert doc["c"] == False  # noqa: E712
    assert doc["a"] != False  # noqa: E712


def test_bool_item_not_equal_other_types():
    assert Bool.__eq__(parse("a = true")["a"], 1) is NotImplemented
    assert parse("a = true")["a"] != "true"
