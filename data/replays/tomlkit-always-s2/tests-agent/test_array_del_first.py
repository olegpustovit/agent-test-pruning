import tomlkit


def test_delete_first_item_without_indent():
    doc = tomlkit.parse("a = [1,2,3]")
    del doc["a"][0]
    assert doc.as_string() == "a = [2,3]"
    assert doc["a"] == [2, 3]


def test_delete_first_item_with_space_indent():
    doc = tomlkit.parse("a = [1, 2, 3]")
    del doc["a"][0]
    assert doc.as_string() == "a = [2, 3]"


def test_delete_first_item_keeps_newline_indent():
    doc = tomlkit.parse("a = [\n  1,\n  2,\n]")
    del doc["a"][0]
    assert doc["a"] == [2]


def test_delete_all_items_without_indent():
    doc = tomlkit.parse("a = [1,2]")
    del doc["a"][0]
    del doc["a"][0]
    assert doc["a"] == []
