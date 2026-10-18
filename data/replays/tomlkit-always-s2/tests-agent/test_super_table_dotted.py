import tomlkit


def test_dotted_only_child_not_super_table():
    doc = tomlkit.parse("[a]\nb.c = 1\n")
    assert not doc["a"].is_super_table()
    assert tomlkit.dumps(doc) == "[a]\nb.c = 1\n"


def test_dotted_only_child_header_kept_on_roundtrip():
    text = "[tool.a]\nb.c.d = 1\n"
    doc = tomlkit.parse(text)
    assert not doc["tool"]["a"].is_super_table()
    assert tomlkit.dumps(doc) == text


def test_real_subtable_is_super_table():
    doc = tomlkit.parse("[a.b]\nc = 1\n")
    assert doc["a"].is_super_table()
    assert not doc["a"]["b"].is_super_table()


def test_inline_table_child_not_super_table():
    doc = tomlkit.parse("[a]\nb = {c = 1}\n")
    assert not doc["a"].is_super_table()


def test_aot_only_child_is_super_table():
    doc = tomlkit.parse("[[a.b]]\nc = 1\n")
    assert doc["a"].is_super_table()


def test_multiple_children_not_super_table():
    doc = tomlkit.parse("[a]\nx = 1\n[a.b]\nc = 1\n")
    assert not doc["a"].is_super_table()
