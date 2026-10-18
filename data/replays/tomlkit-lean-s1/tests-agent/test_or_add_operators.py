import tomlkit


def test_document_ior():
    doc = tomlkit.parse("a = 1\n")
    doc |= {"b": 2}
    assert doc["a"] == 1
    assert doc["b"] == 2
    assert tomlkit.loads(tomlkit.dumps(doc)) == {"a": 1, "b": 2}


def test_table_or_and_ior():
    doc = tomlkit.parse("[t]\na = 1\n")
    merged = doc["t"] | {"b": 2}
    assert merged == {"a": 1, "b": 2}
    assert "b" not in doc["t"]
    doc["t"] |= {"c": 3}
    assert doc["t"]["c"] == 3
    assert "c" in tomlkit.dumps(doc)


def test_array_add_and_iadd():
    doc = tomlkit.parse("a = [1, 2]\n")
    assert doc["a"] + [3] == [1, 2, 3]
    assert doc["a"] == [1, 2]
    doc["a"] += [3, 4]
    assert doc["a"] == [1, 2, 3, 4]
    assert "[1, 2, 3, 4]" in tomlkit.dumps(doc)
