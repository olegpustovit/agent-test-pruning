import tomlkit


def test_replace_last_table_keeps_trailing_newline():
    doc = tomlkit.parse("[a]\nx = 1\n\n[b]\ny = 2\n\n")
    doc["b"] = {"y": 3}
    assert doc.as_string() == "[a]\nx = 1\n\n[b]\ny = 3\n\n"


def test_replace_last_table_without_trailing_newline_unchanged():
    doc = tomlkit.parse("[a]\nx = 1\n\n[b]\ny = 2\n")
    doc["b"] = {"y": 3}
    assert doc.as_string() == "[a]\nx = 1\n\n[b]\ny = 3\n"


def test_replace_middle_table_keeps_separator():
    doc = tomlkit.parse("[a]\nx = 1\n\n[b]\ny = 2\n")
    doc["a"] = {"x": 5}
    assert doc.as_string() == "[a]\nx = 5\n\n[b]\ny = 2\n"


def test_replace_with_non_table_value():
    doc = tomlkit.parse("[a]\nx = 1\n\n[b]\ny = 2\n\n")
    doc["b"] = 1
    assert doc["b"] == 1
