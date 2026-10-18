import tomlkit

from tomlkit import key


def test_append_dotted_keys_after_deleting_only_item():
    # Deleting leaves a Null placeholder, so the first dotted super table is
    # inserted via _insert_at and _table_keys stays empty (#332).
    doc = tomlkit.document()
    doc["x"] = 1
    del doc["x"]
    doc.append(key(["a", "b"]), 1)
    doc.append(key(["a", "c"]), 2)

    assert doc.as_string() == "a.b = 1\na.c = 2\n"
    assert doc.unwrap() == {"a": {"b": 1, "c": 2}}


def test_append_dotted_keys_after_deleting_in_parsed_doc():
    doc = tomlkit.parse("x = 1\n")
    del doc["x"]
    doc.append(key(["a", "b"]), 1)
    doc.append(key(["a", "c"]), 2)

    assert doc.unwrap() == {"a": {"b": 1, "c": 2}}
    assert tomlkit.parse(doc.as_string()).unwrap() == {"a": {"b": 1, "c": 2}}


def test_append_dotted_keys_in_table_after_delete():
    t = tomlkit.table()
    t["x"] = 1
    del t["x"]
    t.append(key(["a", "b"]), 1)
    t.append(key(["a", "c"]), 2)

    assert t.unwrap() == {"a": {"b": 1, "c": 2}}
