import tomlkit


def test_document_ior():
    doc = tomlkit.parse("a = 1\n")
    doc |= {"b": 2}
    assert doc["a"] == 1
    assert doc["b"] == 2
    assert tomlkit.dumps(doc) == "a = 1\nb = 2\n"


def test_document_or_does_not_mutate():
    doc = tomlkit.parse("a = 1\n")
    new = doc | {"b": 2}
    assert new["b"] == 2
    assert "b" not in doc


def test_table_ior_and_or():
    doc = tomlkit.parse("[t]\na = 1\n")
    new = doc["t"] | {"b": 2}
    assert new["b"] == 2
    assert "b" not in doc["t"]
    doc["t"] |= {"c": 3}
    assert doc["t"]["c"] == 3
    assert "c = 3" in tomlkit.dumps(doc)


def test_inline_table_ior():
    doc = tomlkit.parse("t = {a = 1}\n")
    doc["t"] |= {"b": 2}
    assert tomlkit.parse(tomlkit.dumps(doc))["t"] == {"a": 1, "b": 2}


def test_array_add_and_iadd():
    doc = tomlkit.parse("a = [1, 2]\n")
    new = doc["a"] + [3]
    assert list(new) == [1, 2, 3]
    assert list(doc["a"]) == [1, 2]
    doc["a"] += [4, 5]
    assert list(doc["a"]) == [1, 2, 4, 5]
    assert tomlkit.parse(tomlkit.dumps(doc))["a"] == [1, 2, 4, 5]
