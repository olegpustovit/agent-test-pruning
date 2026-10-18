import tomlkit


def test_unwrap_keeps_order_after_replace():
    doc = tomlkit.parse("a = 1\nb = 2\nc = 3\n")
    doc["b"] = 9
    assert tomlkit.dumps(doc) == "a = 1\nb = 9\nc = 3\n"
    assert list(doc.keys()) == ["a", "b", "c"]
    assert list(doc.unwrap()) == ["a", "b", "c"]
    assert doc.unwrap() == {"a": 1, "b": 9, "c": 3}


def test_unwrap_keeps_order_after_replace_in_table():
    doc = tomlkit.parse("[t]\na = 1\nb = 2\nc = 3\n")
    doc["t"]["a"] = 7
    assert list(doc["t"].unwrap()) == ["a", "b", "c"]


def test_unwrap_follows_body_when_replacement_moves():
    doc = tomlkit.parse("a = 1\nb = 2\nc = 3\n")
    doc["a"] = {"x": 1}
    assert list(doc.keys()) == list(doc.unwrap())
    assert doc.unwrap() == {"b": 2, "c": 3, "a": {"x": 1}}
