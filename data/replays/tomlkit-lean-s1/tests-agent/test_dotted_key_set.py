import tomlkit

from tomlkit import key


def test_add_multiple_dotted_keys_to_empty_document():
    doc = tomlkit.document()
    doc.add(key(["a", "b"]), 1)
    doc.add(key(["a", "c"]), 2)

    assert doc.as_string() == "a.b = 1\na.c = 2\n"
    assert doc["a"]["b"] == 1
    assert doc["a"]["c"] == 2


def test_add_dotted_key_to_table_in_parsed_document():
    doc = tomlkit.parse("[tool]\na.b = 1\n")
    doc["tool"].add(key(["a", "c"]), 2)

    assert doc.as_string() == "[tool]\na.b = 1\na.c = 2\n"
    assert doc["tool"]["a"] == {"b": 1, "c": 2}


def test_add_dotted_key_to_new_table():
    table = tomlkit.table()
    table.add(key(["a", "b"]), 1)
    table.add(key(["a", "c"]), 2)

    assert table.as_string() == "a.b = 1\na.c = 2\n"
