import tomlkit


def test_multiple_subtables_is_super_table():
    doc = tomlkit.parse("[a.b]\nx = 1\n[a.c]\ny = 2\n")
    assert doc["a"].is_super_table()
    assert not doc["a"]["b"].is_super_table()


def test_mixed_table_and_aot_is_super_table():
    doc = tomlkit.parse("[[a.b]]\nx = 1\n[a.c]\ny = 2\n")
    assert doc["a"].is_super_table()


def test_value_child_not_super_table():
    doc = tomlkit.parse("[a]\nz = 1\n[a.b]\nx = 1\n[a.c]\ny = 2\n")
    assert not doc["a"].is_super_table()


def test_dotted_child_not_super_table():
    doc = tomlkit.parse("[a]\nb.c = 1\n[a.d]\ny = 2\n")
    assert not doc["a"].is_super_table()


def test_empty_table_not_super_table():
    assert not tomlkit.table().is_super_table()


def test_no_empty_header_dumped():
    text = "[a.b]\nx = 1\n[a.c]\ny = 2\n"
    doc = tomlkit.parse(text)
    assert doc.as_string() == text
    assert tomlkit.dumps(doc) == text


def test_built_multiple_subtables_no_empty_header():
    doc = tomlkit.document()
    a = tomlkit.table()
    a.add("b", {"x": 1})
    a.add("c", {"y": 2})
    doc["a"] = a
    out = tomlkit.dumps(doc)
    assert "[a]" not in out
    assert "[a.b]" in out and "[a.c]" in out
    assert tomlkit.parse(out) == {"a": {"b": {"x": 1}, "c": {"y": 2}}}
