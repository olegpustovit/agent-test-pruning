import tomlkit


def test_plain_value_added_before_first_table_has_blank_line():
    doc = tomlkit.parse("a = 1\n[t]\nb = 2\n")
    doc["c"] = 3
    assert doc.as_string() == "a = 1\nc = 3\n\n[t]\nb = 2\n"


def test_added_value_before_indented_table():
    doc = tomlkit.parse("a = 1\n  [t]\nb = 2\n")
    doc["c"] = 3
    assert doc.as_string() == "a = 1\nc = 3\n\n  [t]\nb = 2\n"


def test_existing_blank_line_not_doubled():
    doc = tomlkit.parse("a = 1\n\n[t]\nb = 2\n")
    doc["c"] = 3
    assert doc.as_string() == "a = 1\nc = 3\n\n[t]\nb = 2\n"


def test_roundtrip_after_add():
    doc = tomlkit.parse("a = 1\n[t]\nb = 2\n")
    doc["c"] = 3
    again = tomlkit.parse(doc.as_string())
    assert again == {"a": 1, "c": 3, "t": {"b": 2}}
