import tomlkit


def test_unwrap_out_of_order_tables_merged():
    doc = tomlkit.parse("[a.b]\nx = 1\n[c]\ny = 2\n[a.d]\nz = 3\n[a]\nw = 4\n")
    assert doc.unwrap() == {
        "a": {"b": {"x": 1}, "d": {"z": 3}, "w": 4},
        "c": {"y": 2},
    }
    assert list(doc.unwrap()) == ["a", "c"]
    assert type(doc.unwrap()["a"]) is dict


def test_unwrap_table_delegates_with_order():
    doc = tomlkit.parse("[t]\nb = 1\na.x = 2\nc = [1, {k = 1}]\n[[aot]]\nq = 1\n[[aot]]\nq = 2\n")
    assert doc["t"].unwrap() == {"b": 1, "a": {"x": 2}, "c": [1, {"k": 1}]}
    assert list(doc["t"].unwrap()) == ["b", "a", "c"]
    assert doc["aot"].unwrap() == [{"q": 1}, {"q": 2}]


def test_unwrap_out_of_order_inside_table():
    doc = tomlkit.parse("[t]\na.b = 1\nm = 0\na.c = 2\n")
    assert doc["t"].unwrap() == {"a": {"b": 1, "c": 2}, "m": 0}


def test_unwrap_after_mutation():
    doc = tomlkit.parse("a = 1\nb = 2\nc = 3\n")
    del doc["b"]
    doc["b"] = 5
    assert doc.unwrap() == {"a": 1, "c": 3, "b": 5}
    assert list(doc.unwrap()) == ["a", "c", "b"]
