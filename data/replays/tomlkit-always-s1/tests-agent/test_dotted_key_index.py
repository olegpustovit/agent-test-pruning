import copy

import tomlkit


def test_append_dotted_key_to_copied_table_does_not_raise():
    # A copied container has an empty ``_table_keys`` list; merging super
    # tables must not index into it for dotted keys.
    doc = tomlkit.parse("[a.b]\nx = 1\n")
    table = copy.copy(doc["a"])
    table.append(tomlkit.key(["b", "c"]), 2)
    assert table["b"]["c"] == 2


def test_set_nested_value_on_copied_document():
    doc = copy.copy(tomlkit.parse("[a.b]\nx = 1\n"))
    doc["a"]["b"]["c"] = 2
    assert tomlkit.loads(doc.as_string())["a"]["b"] == {"x": 1, "c": 2}


def test_set_dotted_key_on_parsed_table():
    doc = tomlkit.parse("[tool]\n[tool.a.b]\nx = 1\n")
    doc["tool"]["a"]["c"] = 2
    assert tomlkit.loads(doc.as_string())["tool"]["a"]["c"] == 2
