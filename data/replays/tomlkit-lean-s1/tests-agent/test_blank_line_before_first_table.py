import tomlkit


def test_plain_value_added_before_first_table_gets_blank_line():
    doc = tomlkit.parse("[tool]\na = 1\n")
    doc["x"] = 1

    assert doc.as_string() == "x = 1\n\n[tool]\na = 1\n"
    assert tomlkit.parse(doc.as_string()) == {"x": 1, "tool": {"a": 1}}


def test_multiple_plain_values_added_before_first_table():
    doc = tomlkit.parse("[tool]\na = 1\n")
    doc["x"] = 1
    doc["y"] = 2

    assert doc.as_string() == "x = 1\ny = 2\n\n[tool]\na = 1\n"


def test_existing_blank_line_before_table_not_duplicated():
    doc = tomlkit.parse("a = 1\n\n[tool]\nb = 1\n")
    doc["x"] = 1

    assert doc.as_string() == "a = 1\nx = 1\n\n[tool]\nb = 1\n"
