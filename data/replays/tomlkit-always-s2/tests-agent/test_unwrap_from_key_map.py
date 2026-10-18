import tomlkit


def test_unwrap_basic_order_and_types():
    doc = tomlkit.parse('b = 1\na = "x"\n[t]\nz = [1, 2]\ny = {k = 1}\n')
    result = doc.unwrap()
    assert result == {"b": 1, "a": "x", "t": {"z": [1, 2], "y": {"k": 1}}}
    assert list(result) == ["b", "a", "t"]
    assert list(result["t"]) == ["z", "y"]
    assert type(result["b"]) is int
    assert type(result["t"]) is dict


def test_unwrap_dotted_and_quoted_keys():
    doc = tomlkit.parse('a.b.c = 1\n"x y" = 2\n[t."q.r"]\nv = 3\n')
    assert doc.unwrap() == {"a": {"b": {"c": 1}}, "x y": 2, "t": {"q.r": {"v": 3}}}


def test_unwrap_array_of_tables():
    doc = tomlkit.parse("[[a]]\nx = 1\n[[a]]\nx = 2\n")
    assert doc.unwrap() == {"a": [{"x": 1}, {"x": 2}]}


def test_unwrap_out_of_order_tables_merged():
    doc = tomlkit.parse("[a.b]\nx = 1\n[c]\ny = 2\n[a.d]\nz = 3\n")
    result = doc.unwrap()
    assert result == {"a": {"b": {"x": 1}, "d": {"z": 3}}, "c": {"y": 2}}
    assert list(result) == ["a", "c"]


def test_unwrap_out_of_order_dotted_keys():
    doc = tomlkit.parse("a.x = 1\nb = 2\na.y = 3\n")
    assert doc.unwrap() == {"a": {"x": 1, "y": 3}, "b": 2}


def test_table_unwrap_out_of_order_inside_table():
    doc = tomlkit.parse("[t]\na.x = 1\nb = 2\na.y = 3\n")
    assert doc["t"].unwrap() == {"a": {"x": 1, "y": 3}, "b": 2}
    assert doc.unwrap() == {"t": {"a": {"x": 1, "y": 3}, "b": 2}}


def test_unwrap_after_mutation():
    doc = tomlkit.parse("a = 1\nb = 2\nc = 3\n")
    del doc["b"]
    doc["d"] = 4
    doc["a"] = 10
    assert doc.unwrap() == {"a": 10, "c": 3, "d": 4}


def test_unwrap_empty():
    assert tomlkit.document().unwrap() == {}
    assert tomlkit.table().unwrap() == {}


def test_unwrap_built_table():
    t = tomlkit.table()
    t.add("a", 1)
    t["b"] = {"c": [1, {"d": 2}]}
    result = t.unwrap()
    assert result == {"a": 1, "b": {"c": [1, {"d": 2}]}}
    assert type(result["b"]["c"][1]) is dict
